import asyncio
import hashlib
import hmac
import json
import os
import uuid

from flask import Flask, jsonify, request

from observability.health import health_snapshot
from observability.metrics import increment
from core.queue.durable import DurableQueue

try:
    from core.persistence.supabase_tasks import store as supabase_tasks
except Exception:
    supabase_tasks = None

app = Flask(__name__)


def _production_cloud_store():
    return bool(
        os.environ.get("VERCEL")
        and supabase_tasks is not None
        and supabase_tasks.configured
    )


def _safe_error_message(error: Exception) -> str:
    message = str(error).replace("\n", " ")[:500]
    for value in (
        os.environ.get("A1OS_EXECUTE_SECRET", ""),
        os.environ.get("A1OS_WORKER_SECRET", ""),
        os.environ.get("SUPABASE_SECRET_KEY", ""),
    ):
        if value:
            message = message.replace(value, "[REDACTED]")
    return message


@app.get("/")
def root():
    return jsonify({"service": "a1os-api", "status": "online", "version": "1.0.0"})


@app.get("/ping")
def ping():
    return jsonify({"ping": "pong"})


@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "a1os-api"})


@app.get("/ready")
def ready():
    cloud = _production_cloud_store()
    return jsonify({
        "status": "ready" if cloud else "degraded",
        "service": "a1os-api",
        "execution_mode": "cloud-queue" if cloud else "serverless-safe",
        "persistence": "supabase" if cloud else "local",
    })


@app.get("/v1/health")
def health_check():
    snapshot = health_snapshot()
    database_integrity = snapshot.get("database_integrity")
    if database_integrity is None:
        database = snapshot.get("database", {})
        if isinstance(database, dict):
            database_integrity = database.get("integrity")
    snapshot["database_integrity"] = database_integrity
    snapshot["persistence"] = "supabase" if _production_cloud_store() else "local"
    snapshot["status"] = "healthy" if _production_cloud_store() else (
        "healthy" if database_integrity == "ok" else "degraded"
    )
    snapshot["version"] = "1.0.0"
    return jsonify(snapshot)


@app.get("/v1/tasks/<task_id>")
def get_task(task_id: str):
    try:
        if _production_cloud_store():
            row = supabase_tasks.get_task(task_id)
            if row is None:
                return jsonify({"detail": "Task not found"}), 404
            return jsonify(row)

        row = DurableQueue.get(task_id)
        if row is None:
            return jsonify({"detail": "Task not found"}), 404
        return jsonify({
            "task_id": row["task_id"],
            "target": row["target"],
            "role": row["role"],
            "action": row["action"],
            "status": row["status"],
            "attempts": row["attempts"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "completed_at": row["completed_at"],
            "error": row["error"],
        })
    except Exception:
        app.logger.exception("A1OS task lookup failed")
        return jsonify({"detail": "Task lookup failed"}), 503


@app.post("/v1/execute")
def execute_task():
    secret = os.environ.get("A1OS_EXECUTE_SECRET")
    if not secret:
        return jsonify({"detail": "Execution authentication is not configured"}), 503

    signature = request.headers.get("X-Signature")
    if not signature:
        return jsonify({"detail": "Execution signature required"}), 401

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"detail": "JSON object payload required"}), 422

    required = ("target", "role", "action", "data")
    if any(key not in payload for key in required):
        return jsonify({"detail": "Payload requires target, role, action, and data"}), 422

    canonical = json.dumps(
        {key: payload[key] for key in required},
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    expected = hmac.new(secret.encode("utf-8"), canonical, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature.strip().lower(), expected.lower()):
        return jsonify({"detail": "Invalid execution signature"}), 403

    try:
        if _production_cloud_store():
            task_id = str(uuid.uuid4())
            supabase_tasks.insert_task(
                task_id=task_id,
                target=payload["target"],
                role=payload["role"],
                action=payload["action"],
                data=payload["data"],
            )
            increment("api.execute.accepted", f"target={payload['target']}")
            return jsonify({
                "status": "accepted",
                "task_id": task_id,
                "execution_mode": "cloud-queue",
            }), 202

        from core.state import system

        memory_key = f"task_{payload['target']}_{payload['action']}"
        system.memory.store(
            key=memory_key,
            value={"role": payload["role"], "data": payload["data"]},
            memory_type="short",
        )
        entity_id = system.knowledge.add_entity(
            entity_type="api_execution_event",
            attributes={
                "target": payload["target"],
                "action": payload["action"],
                "role": payload["role"],
            },
        )
        task_id = DurableQueue.enqueue(
            target=payload["target"],
            role=payload["role"],
            action=payload["action"],
            data=payload["data"],
            task_id=entity_id,
        )
        increment("api.execute.accepted", f"target={payload['target']}")
        asyncio.run(system.runtime.execute(task_id=task_id, payload=payload))
        return jsonify({"status": "accepted", "task_id": task_id})
    except Exception as error:
        app.logger.error(
            "A1OS execution failed: error_type=%s error=%s",
            type(error).__name__,
            _safe_error_message(error),
        )
        return jsonify({"detail": "Execution backend unavailable"}), 503


@app.post("/v1/worker/run")
def run_cloud_worker():
    """Process a bounded batch of cloud tasks; intended for an authenticated scheduler."""
    if not _production_cloud_store():
        return jsonify({"detail": "Cloud task store is not configured"}), 503

    secret = os.environ.get("A1OS_WORKER_SECRET")
    supplied = request.headers.get("X-A1OS-Worker-Token", "")
    if not secret:
        return jsonify({"detail": "Worker authentication is not configured"}), 503
    if not supplied or not hmac.compare_digest(supplied, secret):
        return jsonify({"detail": "Worker authentication failed"}), 401

    body = request.get_json(silent=True) or {}
    try:
        limit = max(1, min(int(body.get("limit", 3)), 5))
    except (TypeError, ValueError):
        return jsonify({"detail": "limit must be an integer from 1 to 5"}), 422

    try:
        from core.state import system

        runtime = getattr(system, "runtime", None)
        if runtime is None:
            return jsonify({"detail": "A1OS runtime is unavailable"}), 503

        results = []
        for row in DurableQueue.pending(limit=limit):
            task_id = str(row["task_id"])
            payload = {
                "target": row["target"],
                "role": row["role"],
                "action": row["action"],
            }
            data = row.get("payload", {})
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except ValueError:
                    data = {}
            if isinstance(data, dict):
                payload.update(data)

            result = asyncio.run(runtime.execute(task_id=task_id, payload=payload))
            results.append(result)

        return jsonify({"status": "processed", "count": len(results), "results": results})
    except Exception as error:
        app.logger.error(
            "A1OS cloud worker failed: error_type=%s error=%s",
            type(error).__name__,
            _safe_error_message(error),
        )
        return jsonify({"detail": "Cloud worker execution failed"}), 503


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.exception("A1OS API error", exc_info=error)
    return jsonify({"detail": "Internal server error"}), 500

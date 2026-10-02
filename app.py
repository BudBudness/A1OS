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


@app.post("/v1/e2e-verify-7f4c9e2a")
def e2e_verify():
    """Temporary production queue verification; remove after E2E check."""
    try:
        if not _production_cloud_store():
            return jsonify({"detail": "Cloud store unavailable"}), 503
        task_id = str(uuid.uuid4())
        payload = {
            "target": "a1os",
            "role": "system",
            "action": "e2e_queue_verification",
            "data": {"source": "temporary-server-side-verification"},
        }
        try:
            supabase_tasks.insert_task(
                task_id=task_id,
                target=payload["target"],
                role=payload["role"],
                action=payload["action"],
                data=payload["data"],
            )
        except Exception as error:
            return jsonify({
                "verified": False,
                "stage": "insert",
                "error_type": type(error).__name__,
                "error": _safe_error_message(error),
            }), 503
        try:
            row = supabase_tasks.get_task(task_id)
        except Exception as error:
            return jsonify({
                "verified": False,
                "stage": "read",
                "error_type": type(error).__name__,
                "error": _safe_error_message(error),
            }), 503
        return jsonify({"verified": row is not None, "task": row}), 200
    except Exception as error:
        app.logger.error(
            "A1OS temporary E2E verification failed: error_type=%s error=%s",
            type(error).__name__,
            _safe_error_message(error),
        )
        return jsonify({"detail": "E2E verification failed"}), 503


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


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.exception("A1OS API error", exc_info=error)
    return jsonify({"detail": "Internal server error"}), 500

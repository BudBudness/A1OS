import asyncio
import hashlib
import hmac
import json
import os

from flask import Flask, jsonify, request

from observability.health import health_snapshot
from observability.metrics import increment
from core.queue.durable import DurableQueue

app = Flask(__name__)


@app.get("/")
def root():
    return jsonify({
        "service": "a1os-api",
        "status": "online",
        "version": "1.0.0",
    })


@app.get("/ping")
def ping():
    return jsonify({"ping": "pong"})


@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "a1os-api"})


@app.get("/ready")
def ready():
    return jsonify({
        "status": "ready",
        "service": "a1os-api",
        "execution_mode": "serverless-safe",
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
    snapshot["status"] = "healthy" if database_integrity == "ok" else "degraded"
    snapshot["version"] = "1.0.0"
    return jsonify(snapshot)


@app.get("/v1/tasks/<task_id>")
def get_task(task_id: str):
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


@app.post("/v1/execute")
def execute_task():
    secret = os.environ.get("A1OS_EXECUTE_SECRET")
    if not secret:
        return jsonify({
            "detail": "Execution authentication is not configured"
        }), 503

    signature = request.headers.get("X-Signature")
    if not signature:
        return jsonify({"detail": "Execution signature required"}), 401

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"detail": "JSON object payload required"}), 422

    required = ("target", "role", "action", "data")
    if any(key not in payload for key in required):
        return jsonify({
            "detail": "Payload requires target, role, action, and data"
        }), 422

    canonical = json.dumps(
        {
            "target": payload["target"],
            "role": payload["role"],
            "action": payload["action"],
            "data": payload["data"],
        },
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")

    expected = hmac.new(
        secret.encode("utf-8"),
        canonical,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature.strip().lower(), expected.lower()):
        return jsonify({"detail": "Invalid execution signature"}), 403

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

    asyncio.run(
        system.runtime.execute(
            task_id=task_id,
            payload=payload,
        )
    )

    return jsonify({"status": "accepted", "task_id": task_id})


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.exception("A1OS API error", exc_info=error)
    return jsonify({"detail": "Internal server error"}), 500

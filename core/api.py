from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Any
import asyncio
import json
from observability.health import health_snapshot
from observability.metrics import increment
from core.queue.durable import DurableQueue

app = FastAPI(title="A1OS Core API", version="1.0.0")

class ExecutePayload(BaseModel):
    target: str
    role: str
    action: str
    data: Any

@app.get("/ping")
async def ping():
    return {"ping": "pong"}

@app.get("/v1/health")
async def health_check():
    snapshot = health_snapshot()
    database_integrity = snapshot.get("database_integrity")
    if database_integrity is None:
        database = snapshot.get("database", {})
        if isinstance(database, dict):
            database_integrity = database.get("integrity")
    snapshot["database_integrity"] = database_integrity
    snapshot["status"] = "healthy" if database_integrity == "ok" else "degraded"
    snapshot["version"] = "1.0.0"
    return snapshot

@app.get("/v1/tasks/{task_id}")
async def get_task(task_id: str):
    row = DurableQueue.get(task_id)

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
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
    }


@app.post("/v1/execute")
async def execute_task(payload: ExecutePayload, x_signature: str = Header(None)):
    """
    Public execution boundary.

    Authentication MUST succeed before any A1OS state, knowledge,
    queue, or runtime side effect occurs.

    Signature format:
        HMAC-SHA256(secret, raw_payload_json)
    supplied as hexadecimal X-Signature.

    Secret:
        A1OS_EXECUTE_SECRET environment variable.

    Missing secret/signature or invalid signature fails closed.
    """
    import os
    import hmac
    import hashlib

    secret = os.environ.get("A1OS_EXECUTE_SECRET")
    if not secret:
        raise HTTPException(
            status_code=503,
            detail="Execution authentication is not configured",
        )

    if not x_signature:
        raise HTTPException(
            status_code=401,
            detail="Execution signature required",
        )

    raw_dict = payload.dict()
    canonical = json.dumps(
        raw_dict,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")

    expected = hmac.new(
        secret.encode("utf-8"),
        canonical,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(
        x_signature.strip().lower(),
        expected.lower(),
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid execution signature",
        )

    from core.state import system

    memory_key = f"task_{payload.target}_{payload.action}"
    system.memory.store(
        key=memory_key,
        value={"role": payload.role, "data": payload.data},
        memory_type="short",
    )

    entity_id = system.knowledge.add_entity(
        entity_type="api_execution_event",
        attributes={
            "target": payload.target,
            "action": payload.action,
            "role": payload.role,
        },
    )

    task_id = DurableQueue.enqueue(
        target=payload.target,
        role=payload.role,
        action=payload.action,
        data=payload.data,
        task_id=entity_id,
    )

    increment("api.execute.accepted", f"target={payload.target}")
    asyncio.create_task(
        system.runtime.execute(
            task_id=task_id,
            payload=raw_dict,
        )
    )

    return {"status": "accepted", "task_id": task_id}

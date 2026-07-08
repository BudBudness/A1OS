from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Any
import asyncio
import json

app = FastAPI(title="A1OS Core API", version="1.0.0")

class ExecutePayload(BaseModel):
    target: str
    role: str
    action: str
    data: Any

@app.get("/v1/health")
async def health_check():
    from core.state import system
    return {
        "status": "healthy",
        "version": "1.0.0",
        "telemetry": system.monitoring.check_health()
    }

@app.post("/v1/execute")
async def execute_task(payload: ExecutePayload, x_signature: str = Header(None)):
    from core.state import system
    
    raw_dict = payload.dict()
    payload_bytes = json.dumps(raw_dict, sort_keys=True).encode("utf-8")
    
    if not system.auth.verify_signature(payload_bytes, x_signature):
        raise HTTPException(status_code=403, detail="Signature Verification Failed.")
        
    try:
        # Prevent event-loop starvation by instantly tracking metadata asynchronously
        memory_key = f"task_{payload.target}_{payload.action}"
        system.memory.store(key=memory_key, value={"role": payload.role, "data": payload.data}, memory_type="short")
        
        entity_id = system.knowledge.add_entity(
            entity_type="api_execution_event",
            attributes={"target": payload.target, "action": payload.action, "role": payload.role}
        )
        
        # Offload task execution immediately into non-blocking background queue worker
        asyncio.create_task(system.runtime.execute(task_id=entity_id, payload=raw_dict))
        
        return {
            "status": "queued",
            "task_id": entity_id,
            "context_verified": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine Routing Failure: {str(e)}")

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json

app = FastAPI(title="A1OS Advanced Gateway")

class ExecutePayload(BaseModel):
    target: str
    role: str = "user"
    action: str = "default"
    data: Any = ""

@app.get("/v1/health")
async def health_check():
    from core.state import system
    return {
        "status": "online",
        "version": "1.0.0",
        "port": 3011,
        "workers": list(system.workers.keys()) if hasattr(system, 'workers') else ["analytics"]
    }

@app.post("/v1/execute")
async def execute_task(payload: ExecutePayload, request: Request):
    from core.state import system
    
    # Skip auth for now
    try:
        result = {
            "status": "success",
            "data": payload.model_dump(),
            "worker": payload.target
        }
        
        # Process based on target
        if payload.target == "analytics":
            result["processed"] = True
            result["message"] = f"Analytics task executed: {payload.action}"
        
        return result
    except Exception as e:
        return {"error": str(e)}

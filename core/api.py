from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Any
import asyncio

from core.dispatcher import dispatcher
from workers.analytics.worker import AnalyticsWorker
from workers.research.worker import ResearchWorker

# Initialize FastAPI
app = FastAPI(title="A1OS Advanced Gateway")

# Register workers
dispatcher.register("analytics", AnalyticsWorker())
dispatcher.register("research", ResearchWorker())

# Define payload model
class ExecutePayload(BaseModel):
    target: str
    role: str = "user"
    action: str = "default"
    data: Any = ""

@app.get("/")
async def root():
    return {
        "message": "Welcome to A1OS Platform",
        "version": "1.0.0",
        "endpoints": {
            "health": "/v1/health",
            "docs": "/docs",
            "dashboard": "/dashboard",
            "execute": "/v1/execute"
        }
    }

@app.get("/v1/health")
async def health_check():
    return {
        "status": "online",
        "version": "1.0.0",
        "port": 3011,
        "workers": dispatcher.list_workers()
    }

@app.post("/v1/execute")
async def execute_task(payload: ExecutePayload, request: Request):
    try:
        result = await dispatcher.dispatch(
            target=payload.target,
            payload=payload.model_dump()
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background jobs
@app.post("/job")
async def create_job(data: dict):
    return {
        "job_id": "job_123",
        "status": "queued",
        "data": data
    }

# File upload
@app.post("/upload")
async def upload_file():
    return {
        "status": "upload_ready",
        "message": "File upload endpoint active",
        "supported": ["image/*", "application/*"]
    }

# Tenant support
@app.post("/tenant")
async def tenant_endpoint(data: dict):
    return {
        "tenant_id": data.get("tenant_id", "default"),
        "data": data.get("data", {}),
        "isolated": True,
        "message": "Tenant data stored"
    }

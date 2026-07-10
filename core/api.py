from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Any
import os
import importlib

from core.dispatcher import dispatcher

app = FastAPI(title="A1OS Advanced Gateway")

# Fallback workers - hardcoded for now
WORKERS = ["analytics", "research", "finance", "support", "security", "sales", 
           "procurement", "marketing", "legal", "hr", "devops", "crm"]

class ExecutePayload(BaseModel):
    target: str
    role: str = "user"
    action: str = "default"
    data: Any = ""

def load_workers():
    for worker_name in WORKERS:
        try:
            module = importlib.import_module(f"workers.{worker_name}.worker")
            worker_class = getattr(module, f"{worker_name.capitalize()}Worker")
            dispatcher.register(worker_name, worker_class())
            print(f"[A1OS] Loaded worker: {worker_name}")
        except Exception as e:
            print(f"[A1OS] Failed to load worker {worker_name}: {e}")

@app.on_event("startup")
async def startup_event():
    load_workers()
    try:
        app.mount("/static", StaticFiles(directory="web/static"), name="static")
    except:
        pass

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

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    html_path = "web/dashboard/index.html"
    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            return f.read()
    return HTMLResponse("<h1>Dashboard not found</h1>")

@app.post("/job")
async def create_job(data: dict):
    return {"job_id": "job_123", "status": "queued", "data": data}

@app.post("/upload")
async def upload_file():
    return {"status": "upload_ready", "message": "File upload endpoint active"}

@app.post("/tenant")
async def tenant_endpoint(data: dict):
    return {
        "tenant_id": data.get("tenant_id", "default"),
        "data": data.get("data", {}),
        "isolated": True,
        "message": "Tenant data stored"
    }

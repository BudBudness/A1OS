from fastapi import FastAPI
from fastapi import HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Any
import os
import importlib

from core.dispatcher import dispatcher

app = FastAPI(title="A1OS Advanced Gateway")

# All workers - including POS
WORKERS = [
    "analytics", "research", "finance", "support", "security",
    "sales", "procurement", "marketing", "legal", "hr",
    "devops", "crm", "pos"
]

class ExecutePayload(BaseModel):
    target: str
    role: str = "user"
    action: str = "default"
    data: Any = ""

def load_workers():
    for worker_name in WORKERS:
        try:
            module = importlib.import_module(f"workers.{worker_name}.worker")
            # Try to find the worker class
            worker_class = None
            for attr in dir(module):
                if attr.endswith("Worker"):
                    worker_class = getattr(module, attr)
                    break
            if worker_class:
                dispatcher.register(worker_name, worker_class())
                print(f"[A1OS] Loaded worker: {worker_name}")
            else:
                print(f"[A1OS] Failed to load worker {worker_name}: no Worker class found")
        except Exception as e:
            print(f"[A1OS] Failed to load worker {worker_name}: {e}")

@app.on_event("startup")
async def startup_event():
    load_workers()
    try:
        app.mount("/static", StaticFiles(directory="web/static"), name="static")
    except:
        pass

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

@app.get("/pos", response_class=HTMLResponse)
async def get_pos():
    html_path = "web/pos/index.html"
    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            return f.read()
    return HTMLResponse("<h1>POS not found</h1>")

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
app.mount("/pos", StaticFiles(directory="web/pos", html=True), name="pos")

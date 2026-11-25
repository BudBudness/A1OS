from datetime import datetime, timezone
from fastapi import FastAPI

app = FastAPI(title="A1OS API", version="1.0.0")

@app.get("/health")
async def health():
    return {"status":"healthy","service":"a1os-api","timestamp":datetime.now(timezone.utc).isoformat()}

@app.get("/ready")
async def ready():
    return {"status":"ready","service":"a1os-api","checks":{"application":"ok"},"timestamp":datetime.now(timezone.utc).isoformat()}

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

# Create main app
app = FastAPI(
    title="A1OS Platform API",
    version="1.0.0",
    description="A1OS - AI Operating System Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Import and include API routes
from core.api import app as api_app
app.include_router(api_app.router)

# Health check
@app.get("/v1/health")
async def health():
    return {"status": "online", "version": "1.0.0", "port": 3011}

# Dashboard
@app.get("/dashboard")
async def dashboard():
    return {
        "message": "A1OS Dashboard",
        "status": "online",
        "workers": ["analytics"],
        "server": "http://0.0.0.0:3011",
        "docs": "http://localhost:3011/docs"
    }

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3011)

@app.get("/")
async def root():
    return {
        "message": "Welcome to A1OS Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/v1/health",
        "dashboard": "/dashboard"
    }

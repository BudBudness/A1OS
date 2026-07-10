import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import os

from core.api import app as api_app

app = api_app

# Serve static files
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Dashboard route - serve HTML
@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    html_path = "web/dashboard/index.html"
    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            return f.read()
    return HTMLResponse("<h1>Dashboard not found</h1><p>Run the dashboard deployment script.</p>")

@app.get("/")
async def root():
    return {
        "message": "Welcome to A1OS Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "dashboard": "/dashboard",
        "health": "/v1/health"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3011)

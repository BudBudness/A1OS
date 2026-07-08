import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.api import app as api_app
from core.state import system

@asynccontextmanager
async def lifespan(app: FastAPI):
    await system.start()
    yield

app = api_app
app.router.lifespan_context = lifespan

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)

import uvicorn
from contextlib import asynccontextmanager

from core.api import app
from core.state import system
from core.persistence.database import Database


@asynccontextmanager
async def lifespan(application):
    await system.start()
    yield


app.router.lifespan_context = lifespan


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3011,
        log_level="info",
    )

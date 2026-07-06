import asyncio
import uvicorn
from gateway import app
from core.runtime import Runtime

runtime = Runtime()

async def boot():
    asyncio.create_task(runtime.run())

@app.on_event("startup")
async def startup():
    await boot()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)

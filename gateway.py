from fastapi import FastAPI, Request
import asyncio
import uuid

app = FastAPI()
runtime = None

@app.on_event("startup")
async def startup():
    global runtime
    from core.runtime import Runtime
    from core.persistence import Persistence
    runtime = Runtime(Persistence())
    asyncio.create_task(runtime.run())

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/v1/command")
async def command(req: Request):
    data = await req.json()
    data["id"] = data.get("id") or str(uuid.uuid4())
    await runtime.dispatch(data)
    return {"status": "queued", "id": data["id"]}

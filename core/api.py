import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.kernel import Kernel

app = FastAPI(title="A1OS API Gateway")
kernel = Kernel()

class TaskPayload(BaseModel):
    target: str
    role: str = "user"
    data: str = ""
    action: str = "default"

@app.post("/v1/execute")
async def execute_task(payload: TaskPayload):
    # Run synchronous kernel processing in an executor to avoid blocking the event loop
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, kernel.process_input, payload.model_dump())
    if isinstance(result, dict) and "error" in result:
        if result["error"] == "Unauthorized":
            raise HTTPException(status_code=403, detail="Unauthorized")
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get("/v1/health")
async def health_check():
    return {"status": "online", "active_workers": list(kernel.workers.keys()), "heartbeats": kernel.heartbeats}

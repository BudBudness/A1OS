from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.kernel import Kernel

app = FastAPI(title="A1OS Advanced Gateway")
kernel = Kernel()

class TaskPayload(BaseModel):
    target: str
    role: str = "user"
    data: str = ""
    action: str = "default"
    tenant_id: str = None
    customer_id: str = None
    profile: dict = {}

@app.post("/v1/execute")
async def execute_task(payload: TaskPayload):
    result = await kernel.process_input_async(payload.model_dump())
    if isinstance(result, dict) and "error" in result:
        if result["error"] == "Unauthorized":
            raise HTTPException(status_code=403, detail="Unauthorized")
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get("/v1/health")
async def health_check():
    return {"status": "online", "active_workers": list(kernel.workers.keys())}

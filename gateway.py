from fastapi import FastAPI, Request, HTTPException
from infra.auth.jwt import verify_token
from infra.observability.metrics import record_event

app = FastAPI()

@app.post("/api/v1/command")
async def command(req: Request):
    token = req.headers.get("authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        verify_token(token.replace("Bearer ", ""))
    except:
        raise HTTPException(status_code=403, detail="Invalid token")

    payload = await req.json()
    record_event()
    return {"status": "queued", "payload": payload}

@app.get("/health")
async def health():
    return {"status": "ok"}

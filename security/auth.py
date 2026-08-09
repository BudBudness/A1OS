from fastapi import Request, HTTPException

API_KEY = "dev-key-change-me"

def verify(request: Request):
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

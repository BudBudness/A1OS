from __future__ import annotations

import asyncio
import os
import shlex
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

ROOT = Path(os.environ.get("A1OS_ROOT", Path.cwd())).resolve()
STATIC = Path(__file__).with_name("static")
SAFE_ROOT = ROOT

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers.update({
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        })
        return response

app = FastAPI(title="A1OS Control Plane", version="2.0.0")
app.add_middleware(SecurityHeadersMiddleware)

class CommandRequest(BaseModel):
    command: str = Field(min_length=1, max_length=500)
    approve: bool = False

class CommandResponse(BaseModel):
    status: str
    command: str
    output: str = ""
    error: str = ""
    returncode: int | None = None
    approval_required: bool = False

class EventHub:
    def __init__(self) -> None:
        self.clients: set[WebSocket] = set()
    async def publish(self, event: dict[str, Any]) -> None:
        dead = []
        for client in self.clients:
            try:
                await client.send_json(event)
            except Exception:
                dead.append(client)
        for client in dead:
            self.clients.discard(client)

hub = EventHub()

ALLOWED_COMMANDS = {
    "python -m compileall .",
    "python3 -m compileall .",
    "python -m pytest",
    "python3 -m pytest",
    "git status --short",
    "git diff --check",
}

def _validate_command(command: str) -> list[str]:
    try:
        parts = shlex.split(command)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid command syntax: {exc}") from exc
    normalized = " ".join(parts)
    if normalized not in ALLOWED_COMMANDS:
        raise HTTPException(status_code=403, detail="Command is not in the control-plane allowlist")
    return parts

async def _execute(parts: list[str]) -> tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(*parts, cwd=str(SAFE_ROOT),
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    return proc.returncode, stdout.decode(errors="replace"), stderr.decode(errors="replace")

@app.get("/")
async def index():
    return FileResponse(STATIC / "index.html")

@app.get("/api/health")
async def health():
    return {"status": "online", "system": "A1OS", "control_plane": "online", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/api/status")
async def status():
    return {"a1os": "online", "human_authority": True, "execution_policy": "approval_gated", "cwd": str(ROOT)}

@app.post("/api/command", response_model=CommandResponse)
async def command(request: CommandRequest):
    command_text = request.command.strip()
    parts = _validate_command(command_text)
    if not request.approve:
        return CommandResponse(status="approval_required", command=command_text, approval_required=True)
    code, output, error = await _execute(parts)
    await hub.publish({"type": "command", "command": command_text, "returncode": code, "timestamp": datetime.now(timezone.utc).isoformat()})
    return CommandResponse(status="success" if code == 0 else "failed", command=command_text, output=output, error=error, returncode=code)

@app.websocket("/ws")
async def websocket(websocket: WebSocket):
    await websocket.accept()
    hub.clients.add(websocket)
    try:
        await websocket.send_json({"type": "connected", "system": "A1OS"})
        while True:
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        hub.clients.discard(websocket)

if STATIC.is_dir():
    app.mount("/ui", StaticFiles(directory=STATIC, html=True), name="ui")

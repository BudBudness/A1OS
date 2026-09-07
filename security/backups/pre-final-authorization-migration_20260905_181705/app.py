from __future__ import annotations

import asyncio
import os
import shlex
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

ROOT = Path(os.environ.get("A1OS_ROOT", Path.cwd())).resolve()
STATIC = Path(__file__).with_name("static")
SAFE_ROOT = ROOT

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(self), geolocation=(), payment=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


app = FastAPI(title="A1OS Control Plane", version="1.0.0")

app.add_middleware(SecurityHeadersMiddleware)

from core.control_plane.jarvis import router as jarvis_router
app.include_router(jarvis_router)


class CommandRequest(BaseModel):
    command: str = Field(min_length=1, max_length=4000)
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


def _validate_command(command: str) -> None:
    dangerous = (
        "rm -rf /",
        "mkfs",
        "dd if=",
        ":(){ :|:& };:",
        "shutdown",
        "reboot",
    )
    normalized = command.strip().lower()
    if any(item in normalized for item in dangerous):
        raise HTTPException(status_code=403, detail="Command blocked by control-plane policy")


async def _execute(command: str) -> tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        "bash",
        "-lc",
        command,
        cwd=str(SAFE_ROOT),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return proc.returncode, stdout.decode(errors="replace"), stderr.decode(errors="replace")


@app.get("/")
async def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/health")
async def health():
    return {
        "status": "online",
        "system": "A1OS",
        "control_plane": "online",
        "root": str(ROOT),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/status")
async def status():
    return {
        "a1os": "online",
        "termux_linux": "connected",
        "human_authority": True,
        "autonomous_execution": "approval_gated",
        "cwd": str(ROOT),
    }



# SECURITY HARDENING: raw shell execution endpoint retired.
# Execution must use JARVIS/A1OS capability authorization and the
# universal consequence gate. This endpoint intentionally fails closed.
@app.post("/api/command", response_model=CommandResponse)
async def command(request: CommandRequest):
    raise HTTPException(
        status_code=410,
        detail="Raw command execution retired; use authorized A1OS capabilities."
    )

async def command(request: CommandRequest):
    command_text = request.command.strip()
    _validate_command(command_text)

    if not request.approve:
        return CommandResponse(
            status="approval_required",
            command=command_text,
            approval_required=True,
        )

    code, output, error = await _execute(command_text)
    event = {
        "type": "command",
        "command": command_text,
        "returncode": code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await hub.publish(event)

    return CommandResponse(
        status="success" if code == 0 else "failed",
        command=command_text,
        output=output,
        error=error,
        returncode=code,
    )


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


_STATIC = Path(__file__).parent / "static"
if _STATIC.is_dir():
    app.mount("/ui", StaticFiles(directory=_STATIC, html=True), name="ui")

from __future__ import annotations

import asyncio
import os
import shlex
from dataclasses import dataclass
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(prefix="/api/jarvis", tags=["jarvis"])


class CommandRequest(BaseModel):
    command: str


class ApprovalRequest(BaseModel):
    token: str


@dataclass
class PendingCommand:
    command: str


_pending: dict[str, PendingCommand] = {}


def _plan(command: str) -> dict[str, Any]:
    text = command.strip()
    lowered = text.lower()

    if not text:
        return {"intent": "empty", "requires_approval": False}

    if lowered in {"status", "system status", "a1os status", "show status"}:
        return {
            "intent": "status",
            "command": "python3 -m pytest -q",
            "requires_approval": False,
        }

    if lowered in {"stop", "halt", "shutdown a1os", "stop a1os"}:
        return {
            "intent": "stop",
            "command": "pkill -f 'A1OS_RESTORED' || true",
            "requires_approval": True,
        }

    if lowered.startswith(("run ", "execute ", "terminal ", "termux ")):
        parts = text.split(maxsplit=1)
        command_text = parts[1].strip() if len(parts) == 2 else ""
        if not command_text:
            raise HTTPException(status_code=400, detail="Missing command")
        return {
            "intent": "terminal",
            "command": command_text,
            "requires_approval": True,
        }

    return {
        "intent": "unknown",
        "command": None,
        "requires_approval": False,
        "message": "Command understood only as a plan. No execution performed.",
    }


@router.post("/plan")
async def plan(request: CommandRequest):
    return _plan(request.command)


@router.post("/approve")
async def approve(request: ApprovalRequest):
    command = _pending.pop(request.token, None)

    if command is None:
        raise HTTPException(status_code=404, detail="Approval token not found")

    proc = await asyncio.create_subprocess_exec(
        "sh",
        "-lc",
        command.command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=os.path.expanduser("~/A1OS_RESTORED"),
    )

    stdout, _ = await proc.communicate()

    return {
        "status": "completed" if proc.returncode == 0 else "failed",
        "exit_code": proc.returncode,
        "output": stdout.decode(errors="replace"),
    }

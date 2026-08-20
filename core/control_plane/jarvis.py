from __future__ import annotations

import asyncio
import os
import shlex
from dataclasses import dataclass
from typing import Any
from enum import Enum
import secrets

from fastapi import APIRouter, HTTPException
from .execution_broker import ExecutionBroker, ExecutionDenied
from pydantic import BaseModel


router = APIRouter(prefix="/api/jarvis", tags=["jarvis"])

_execution_broker = ExecutionBroker()


class RiskLevel(str, Enum):
    READ = "read"
    EXECUTE = "execute"
    DESTRUCTIVE = "destructive"


class CommandDecision(BaseModel):
    intent: str
    command: str | None = None
    risk: RiskLevel
    requires_approval: bool
    approval_token: str | None = None
    message: str | None = None


_audit_log: list[dict[str, Any]] = []


def _risk_for(intent: str) -> RiskLevel:
    if intent == "status":
        return RiskLevel.READ
    if intent == "stop":
        return RiskLevel.DESTRUCTIVE
    if intent == "terminal":
        return RiskLevel.EXECUTE
    return RiskLevel.READ


def _record(event: str, **data: Any) -> None:
    _audit_log.append({"event": event, **data})




class CommandRequest(BaseModel):
    command: str


class ApprovalRequest(BaseModel):
    token: str


@dataclass
class PendingCommand:
    command: str


_pending: dict[str, PendingCommand] = {}

LITTLE_OAKS_VERTICAL = {
    "name": "little-oaks",
    "runtime": "products/verticals/little-oaks",
    "backend": "a1os-platform-api",
    "core": "a1os-core",
}

def resolve_vertical(name: str) -> dict[str, str]:
    if name == "little-oaks":
        return LITTLE_OAKS_VERTICAL
    raise HTTPException(status_code=404, detail="Vertical not found")



def _plan(command: str) -> dict[str, Any]:
    text = command.strip()
    lowered = text.lower()

    if not text:
        return {"intent": "empty", "requires_approval": False}

    if lowered in {"status", "system status", "a1os status", "show status"}:
        result = {
            "intent": "status",
            "command": "python3 -m pytest -q",
            "risk": RiskLevel.READ,
            "requires_approval": False,
            "approval_token": None,
        }
        _record("planned", requested_command=text, **result)
        return result

    if lowered in {"stop", "halt", "shutdown a1os", "stop a1os"}:
        token = secrets.token_urlsafe(24)
        _pending[token] = PendingCommand(
            "pkill -f 'A1OS_RESTORED' || true"
        )
        result = {
            "intent": "stop",
            "command": "pkill -f 'A1OS_RESTORED' || true",
            "risk": RiskLevel.DESTRUCTIVE,
            "requires_approval": True,
            "approval_token": token,
        }
        _record("approval_required", requested_command=text, **result)
        return result

    if lowered.startswith(("run ", "execute ", "terminal ", "termux ")):
        parts = text.split(maxsplit=1)
        command_text = parts[1].strip() if len(parts) == 2 else ""
        if not command_text:
            raise HTTPException(status_code=400, detail="Missing command")
        token = secrets.token_urlsafe(24)
        _pending[token] = PendingCommand(command_text)
        result = {
            "intent": "terminal",
            "command": command_text,
            "risk": RiskLevel.EXECUTE,
            "requires_approval": True,
            "approval_token": token,
        }
        _record("approval_required", requested_command=text, **result)
        return result

    result = {
        "intent": "unknown",
        "command": None,
        "risk": RiskLevel.READ,
        "requires_approval": False,
        "approval_token": None,
        "message": "Command understood only as a plan. No execution performed.",
    }
    _record("rejected", requested_command=text, **result)
    return result


@router.post("/plan")
async def plan(request: CommandRequest):
    return _plan(request.command)


@router.post("/approve")
async def approve(request: ApprovalRequest):
    command = _pending.pop(request.token, None)

    if command is None:
        raise HTTPException(status_code=404, detail="Approval token not found")

    _record("approved", command=command.command)

    proc = await asyncio.create_subprocess_exec(
        "sh",
        "-lc",
        command.command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=os.path.expanduser("~/A1OS_RESTORED"),
    )

    stdout, _ = await proc.communicate()

    result = {
        "status": "completed" if proc.returncode == 0 else "failed",
        "exit_code": proc.returncode,
        "output": stdout.decode(errors="replace"),
    }
    _record("execution_result", command=command.command, **result)
    return result

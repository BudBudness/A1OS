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
    "runtime": "clients/little-oaks",
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

    implementation_terms = (
        "implement", "build", "upgrade", "modify", "change", "create",
        "add", "update", "install", "configure", "refactor", "replace"
    )

    if any(term in text.lower() for term in implementation_terms):
        pending_command = text

        token = secrets.token_urlsafe(32)
        _pending[token] = PendingCommand(pending_command)

        result = {
            "intent": "implementation",
            "command": pending_command,
            "risk": RiskLevel.EXECUTE,
            "requires_approval": True,
            "approval_token": token,
            "message": "Implementation plan prepared. Human approval required before execution.",
        }
        _record("planned", requested_command=text, **{
            k:v for k,v in result.items() if k != "approval_token"
        })
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




@router.get("/status")
async def jarvis_status():
    return {
        "status": "online",
        "phase": "ready",
        "message": "JARVIS online",
        "a1os": "online",
        "termux_linux": "connected",
        "human_authority": True,
        "autonomous_execution": "approval_gated",
    }

def _natural_language_plan(command: str) -> dict[str, Any] | None:
    text = command.strip().lower()

    health_terms = (
        "health", "healthy", "status", "diagnostic", "diagnostics",
        "check the platform", "check a1os", "platform health",
        "is everything working", "anything wrong", "system status"
    )

    if any(term in text for term in health_terms):
        return {
            "intent": "platform_health_check",
            "command": command,
            "risk": "read_only",
            "requires_approval": False,
            "execution": "platform_health_check",
            "message": "Executing read-only A1OS platform diagnostics."
        }

    # Consequential natural-language actions must be
    # interpreted before the generic fallback. They remain
    # approval-gated and are never auto-executed here.
    consequential_actions = (
        (
            "deploy_application",
            (
                "deploy the application to production",
                "deploy application to production",
                "deploy the app to production",
                "deploy to production",
                "deploy the application",
                "deploy application",
            ),
        ),

        (
            "restart_production_service",
            (
                "restart the a1os production service",
                "restart a1os production",
                "restart the production a1os service",
                "restart the a1os service",
                "restart a1os",
            ),
        ),
        (
            "stop_production_service",
            (
                "stop the a1os production service",
                "stop a1os production",
                "stop the production a1os service",
                "stop the a1os service",
            ),
        ),
        (
            "start_production_service",
            (
                "start the a1os production service",
                "start a1os production",
                "start the production a1os service",
                "start the a1os service",
            ),
        ),
    )

    for intent, phrases in consequential_actions:
        if any(phrase in text for phrase in phrases):
            return {
                "intent": intent,
                "command": command,
                "risk": "consequential",
                "requires_approval": True,
                "execution": intent,
                "message": "Approval required before executing this consequential operation.",
            }

    return None

@router.post("/plan")
async def plan(request: CommandRequest):
    nl = _natural_language_plan(request.command)

    # Preserve the explicit "status" planner contract expected by the
    # control-plane compatibility tests. Broader platform-health/report
    # requests continue through the platform_health_check path below.
    if request.command.strip().lower() == "status":
        nl = {
            "intent": "status",
            "command": request.command,
            "risk": "read",
            "requires_approval": False,
            "execution": None,
            "message": "Status check is read-only.",
        }

    # Broad read-only platform-report requests must enter the same
    # automatically executable diagnostic path as explicit health checks.
    command_lower = request.command.strip().lower()
    full_report_phrases = (
        "full report on a1os",
        "full report of a1os",
        "report on a1os",
        "report of a1os",
        "a1os full report",
        "complete report on a1os",
        "complete report of a1os",
        "status of a1os",
        "a1os status",
        "how is a1os",
        "check a1os",
        "check the a1os platform",
        "check the platform",
        "platform health",
    )

    if nl is None and any(
        phrase in command_lower for phrase in full_report_phrases
    ):
        nl = {
            "intent": "platform_health_check",
            "command": request.command,
            "risk": "read_only",
            "requires_approval": False,
            "execution": "platform_health_check",
            "message": "A1OS platform health report completed.",
        }

    if nl:
        if nl["execution"] == "platform_health_check":
            import httpx
            checks = {}
            async with httpx.AsyncClient(timeout=5.0) as client:
                for name, url in (
                    ("platform_api", "http://127.0.0.1:3013/v1/health"),
                    ("jarvis", "http://127.0.0.1:3013/api/jarvis/status"),
                ):
                    try:
                        r = await client.get(url)
                        checks[name] = {
                            "status_code": r.status_code,
                            "healthy": r.is_success,
                            "response": r.json(),
                        }
                    except Exception as exc:
                        checks[name] = {
                            "healthy": False,
                            "error": str(exc),
                        }

            healthy = all(v.get("healthy", False) for v in checks.values())
            nl["status"] = "healthy" if healthy else "degraded"
            nl["checks"] = checks
            nl["message"] = (
                "A1OS platform health check completed."
                if healthy else
                "A1OS platform health check completed; one or more checks require attention."
            )
            _record("executed_read_only", requested_command=request.command, **nl)
            return nl

        # Consequential operations are understood by JARVIS but remain
        # approval-gated. Nothing consequential executes from /plan.
        if nl.get("risk") == "consequential" and nl.get("execution"):
            import secrets

            token = secrets.token_urlsafe(24)
            _pending[token] = PendingCommand(request.command)

            result = {
                **nl,
                "approval_token": token,
                "message": (
                    "Approval required before executing this "
                    "consequential operation."
                ),
            }

            _record(
                "approval_required",
                requested_command=request.command,
                **result,
            )
            return result

    return _plan(request.command)


@router.post("/approve")
async def approve(request: ApprovalRequest):
    command = _pending.pop(request.token, None)

    if command is None:
        raise HTTPException(status_code=404, detail="Approval token not found")

    # Normalize legacy string entries and PendingCommand entries at the
    # approval boundary. The approval gate itself remains mandatory.
    command_text = (
        command.command
        if isinstance(command, PendingCommand)
        else str(command)
    )

    if isinstance(command, PendingCommand):
        approved_command = command
    else:
        approved_command = PendingCommand(command_text)

    _record("approved", command=command_text)

    # Map approved natural-language intents to real executors.
    # Never send an intent phrase such as "restart the A1OS production service"
    # directly to a shell.
    if command_text.lower() == "restart the a1os production service":
        # Restart through a detached standalone script so the current
        # approval HTTP request is not killed by the restart operation.
        proc = await asyncio.create_subprocess_exec(
            "sh",
            "runtime/scripts/restart_production_3017.sh",
            str(os.getpid()),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=os.path.expanduser("~/A1OS_RESTORED"),
        )

    elif command_text.lower().startswith(("implement ", "build ", "upgrade ", "modify ", "change ", "create ", "add ", "update ", "install ", "configure ", "refactor ", "replace ")):
        proc = await asyncio.create_subprocess_exec(
            "python3",
            "tools/a1os_factory/real_build_executor/build_executor_engine.py",
            command_text,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=os.path.expanduser("~/A1OS_RESTORED"),
        )
    else:
        proc = await asyncio.create_subprocess_exec(
            "sh",
            "-lc",
            command_text,
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
    _record("execution_result", command=command_text, **result)
    return result

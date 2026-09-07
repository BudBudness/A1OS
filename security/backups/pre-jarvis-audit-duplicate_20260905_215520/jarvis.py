from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any
from enum import Enum
import secrets

from fastapi import APIRouter, HTTPException
from .execution_broker import ExecutionBroker, ExecutionDenied
from pydantic import BaseModel
from core.control_plane.jarvis_ai import JARVISAIInterpreter
from core.state import system as a1os_system


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

_jarvis_ai_interpreter = JARVISAIInterpreter()

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
        # Preserve the terminal intent marker through the approval boundary.
        # The response exposes the normalized command, while the pending
        # command retains the executor-dispatch prefix.
        _pending[token] = PendingCommand(text)
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
    # ---------------------------------------------------------------
    # 1. Deterministic planner ALWAYS gets first priority.
    #    This preserves established JARVIS contracts.
    # ---------------------------------------------------------------
    nl = _natural_language_plan(request.command)

    if request.command.strip().lower() == "status":
        nl = {
            "intent": "status",
            "command": request.command,
            "risk": "read",
            "requires_approval": False,
            "execution": None,
            "message": "Status check is read-only.",
        }

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

    # ---------------------------------------------------------------
    # 2. Existing deterministic executions.
    # ---------------------------------------------------------------
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

            healthy = all(
                value.get("healthy", False)
                for value in checks.values()
            )

            nl["status"] = "healthy" if healthy else "degraded"
            nl["checks"] = checks
            nl["message"] = (
                "A1OS platform health check completed."
                if healthy
                else
                "A1OS platform health check completed; "
                "one or more checks require attention."
            )

            _record(
                "executed_read_only",
                requested_command=request.command,
                **nl,
            )
            return nl

        # Consequential operations remain approval-gated.
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

    # ---------------------------------------------------------------
    # 3. Run the complete deterministic planner.
    #
    #    IMPORTANT:
    #    _plan() recognizes terminal, stop, implementation, status,
    #    etc. BEFORE AI is ever consulted.
    # ---------------------------------------------------------------
    deterministic = _plan(request.command)

    # ---------------------------------------------------------------
    # 4. Explicit capability-information and diagnostics requests
    # must reach semantic interpretation before deterministic broad
    # health matching can terminate the request.
    lowered_request = request.command.strip().lower()

    semantic_priority_terms = (
        "diagnostic",
        "diagnostics",
        "capabilities",
        "what can a1os",
        "what can you do",
        "what are you capable",
    )

    semantic_priority = any(
        term in lowered_request
        for term in semantic_priority_terms
    )

    if deterministic.get("intent") != "unknown" and not semantic_priority:
        return deterministic

    if semantic_priority:
        deterministic = {
            "intent": "unknown",
            "command": None,
            "risk": RiskLevel.READ,
            "requires_approval": False,
            "approval_token": None,
            "message": "Semantic interpretation required.",
        }

    # ---------------------------------------------------------------
    # 4. ONLY genuinely unknown requests reach semantic AI.
    # ---------------------------------------------------------------
    try:
        ai_result = await _jarvis_ai_interpreter.interpret(
            request.command,
            a1os_system.capabilities.list(),
        )

        capability = ai_result.get("capability")
        confidence = float(
            ai_result.get("confidence", 0.0) or 0.0
        )

        if not capability or confidence < 0.80:
            return deterministic

        # AI does NOT determine risk or authorization.
        # The capability itself must pass through A1OS's
        # universal consequence gate.
        arguments = ai_result.get("arguments") or {}

        # AI interprets language only. A1OS decides consequence,
        # authorization, provenance, and whether execution is admitted.
        try:
            gate = a1os_system._universal_consequence_gate(
                capability=capability,
                kwargs=arguments,
            )
            if hasattr(gate, "__await__"):
                gate = await gate
        except Exception as exc:
            _record(
                "semantic_consequence_gate_failed",
                requested_command=request.command,
                capability=capability,
                error=str(exc),
            )
            return {
                "intent": ai_result.get("intent") or capability,
                "command": request.command,
                "capability": capability,
                "arguments": arguments,
                "risk": RiskLevel.READ,
                "requires_approval": True,
                "approval_token": None,
                "execution": "a1os_capability",
                "status": "blocked",
                "error": str(exc),
                "message": "A1OS consequence gate could not authorize execution.",
            }

        classification = gate.get("classification")
        requires_authorization = bool(
            gate.get("requires_authorization", False)
        )
        allowed = bool(gate.get("allowed", False))

        if not allowed or requires_authorization:
            token = secrets.token_urlsafe(32)
            _pending[token] = PendingCommand(
                request.command
            )

            response = {
                "intent": ai_result.get("intent") or capability,
                "command": request.command,
                "capability": capability,
                "arguments": arguments,
                "risk": (
                    RiskLevel.EXECUTE
                    if classification == "consequential"
                    else RiskLevel.READ
                ),
                "requires_approval": True,
                "approval_token": token,
                "execution": "a1os_capability",
                "message": (
                    "Semantic request resolved. Human approval required "
                    "before consequential execution."
                ),
            }

            _record(
                "semantic_approval_required",
                requested_command=request.command,
                **response,
            )
            return response

        response = {
            "intent": ai_result.get("intent") or capability,
            "command": request.command,
            "capability": capability,
            "arguments": arguments,
            "risk": RiskLevel.READ,
            "requires_approval": False,
            "approval_token": None,
            "execution": "a1os_capability",
            "message": "Request semantically resolved by JARVIS.",
        }

        _record(
            "semantic_plan",
            requested_command=request.command,
            **response,
        )

        try:
            result = await a1os_system.execute(
                capability,
                **arguments,
            )
        except Exception as exc:
            _record(
                "semantic_execution_failed",
                requested_command=request.command,
                capability=capability,
                error=str(exc),
            )

            return {
                **response,
                "status": "failed",
                "error": str(exc),
            }

        response["status"] = "completed"
        response["result"] = result

        _record(
            "executed_semantic_capability",
            requested_command=request.command,
            **response,
        )

        return response

    except Exception as exc:
        _record(
            "semantic_plan_failed",
            requested_command=request.command,
            error=str(exc),
        )
        return deterministic


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

    # Map approved natural-language intents to explicit executors.
    # Approved consequential operations MUST NOT fall through to an arbitrary shell.

    command_lower = command_text.strip().lower()

    # ------------------------------------------------------------
    # LEGACY DIRECT EXECUTION RETIRED
    # ------------------------------------------------------------
    # Approval does not grant arbitrary shell authority.
    #
    # Consequential execution must resolve to an explicit A1OS
    # capability and pass:
    #
    #   human approval
    #       -> authorization verification
    #       -> universal consequence gate
    #       -> CapabilityRegistry
    #       -> typed executor
    #
    # Terminal, deploy, restart, build, and arbitrary subprocess
    # execution are intentionally unavailable through this legacy
    # approval endpoint until migrated to capability-bound execution.
    # ------------------------------------------------------------
    # CAPABILITY-BOUND EXECUTION
    # ------------------------------------------------------------
    # Human approval is consumed exactly once above. The approved
    # natural-language command is mapped to a fixed A1OS capability.
    # No shell, arbitrary subprocess, restart, start, or stop path
    # exists here.

    capability = None
    capability_kwargs = {}

    if command_lower in {
        "deploy the application",
        "deploy application",
        "deploy the application to production",
        "deploy application to production",
        "deploy the app to production",
        "deploy to production",
    }:
        capability = "deploy_application"
        capability_kwargs = {"product": "platform"}

    elif command_lower.startswith(
        (
            "implement ",
            "build ",
            "upgrade ",
            "modify ",
            "change ",
            "create ",
            "add ",
            "update ",
            "install ",
            "configure ",
            "refactor ",
            "replace ",
        )
    ):
        capability = "build_change"
        capability_kwargs = {"request": command_text}

    if capability is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Approved command has no registered capability. "
                "No arbitrary executor is available."
            ),
        )

    from core.state import system, HumanApprovalMarker

    approval_marker = HumanApprovalMarker(
        token=request.token,
        capability=capability,
        command=command_text,
        entity_id="primary-device",
        target_action=capability,
    )

    capability_kwargs["_human_approval"] = approval_marker

    try:
        result = await system.execute(
            capability,
            **capability_kwargs,
        )
    except Exception as exc:
        _record(
            "execution_denied",
            command=command_text,
            capability=capability,
            reason=str(exc),
        )
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    _record(
        "execution_result",
        command=command_text,
        capability=capability,
        **result,
    )
    return result

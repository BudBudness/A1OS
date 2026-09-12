from __future__ import annotations

import asyncio
import os
import shlex
from dataclasses import dataclass
from typing import Any


class ExecutionDenied(PermissionError):
    pass


@dataclass(frozen=True)
class ExecutionResult:
    command: str
    exit_code: int
    output: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "command": self.command,
            "exit_code": self.exit_code,
            "output": self.output,
        }


class ExecutionBroker:
    """Human-approved execution boundary between A1OS and Termux/Linux."""

    def __init__(self) -> None:
        self._audit: list[dict[str, Any]] = []

    @property
    def audit(self) -> list[dict[str, Any]]:
        return list(self._audit)

    def _record(self, event: str, **data: Any) -> None:
        self._audit.append({"event": event, **data})

    @staticmethod
    def validate(command: str) -> str:
        command = command.strip()
        if not command:
            raise ValueError("Command is empty")
        if "\x00" in command:
            raise ValueError("NUL byte is not allowed")
        return command

    async def execute(
        self,
        command: str,
        *,
        approved: bool = False,
        authorization: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        command = self.validate(command)

        # SECURITY HARDENING:
        # A boolean approval is never sufficient authority for shell execution.
        # Broker execution requires capability-bound authorization/provenance.
        if not approved or not isinstance(authorization, dict):
            self._record(
                "execution_denied",
                command=command,
                reason="missing_capability_bound_authorization",
            )
            raise ExecutionDenied(
                "Capability-bound authorization is required"
            )

        required = {"capability", "provenance"}
        if not required.issubset(authorization):
            self._record(
                "execution_denied",
                command=command,
                reason="invalid_authorization",
            )
            raise ExecutionDenied(
                "Invalid capability-bound authorization"
            )

        self._record(
            "execution_started",
            command=command,
            capability=authorization["capability"],
        )

        # SECURITY INVARIANT:
        # ExecutionBroker is not a shell gateway.
        #
        # Executable behavior must be represented by an explicit
        # A1OS capability and executed through CapabilityRegistry.
        self._record(
            "execution_denied",
            command=command,
            capability=authorization.get("capability"),
            reason="arbitrary_shell_execution_retired",
        )
        raise ExecutionDenied(
            "Arbitrary shell execution is retired; "
            "execute only through an authorized A1OS capability."
        )

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
        return {"command": self.command, "exit_code": self.exit_code, "output": self.output}


class ExecutionBroker:
    """Human-approved, allowlisted execution boundary."""

    ALLOWED_COMMANDS = {
        "printf approved",
        "printf 'A1OS_BROKER_OK'",
    }

    def __init__(self) -> None:
        self._audit: list[dict[str, Any]] = []

    @property
    def audit(self) -> list[dict[str, Any]]:
        return list(self._audit)

    def _record(self, event: str, **data: Any) -> None:
        self._audit.append({"event": event, **data})

    @classmethod
    def validate(cls, command: str) -> list[str]:
        command = command.strip()
        if not command:
            raise ValueError("Command is empty")
        if "\x00" in command:
            raise ValueError("NUL byte is not allowed")
        try:
            parts = shlex.split(command)
        except ValueError as exc:
            raise ValueError(f"Invalid command syntax: {exc}") from exc
        normalized = " ".join(parts)
        if normalized not in {"printf approved", "printf A1OS_BROKER_OK"}:
            raise PermissionError("Command is not allowlisted")
        return parts

    async def execute(self, command: str, *, approved: bool = False) -> dict[str, Any]:
        raw = command.strip()
        if not approved:
            if not raw:
                raise ValueError("Command is empty")
            self._record("execution_denied", command=raw)
            raise ExecutionDenied("Human approval is required")

        parts = self.validate(raw)
        self._record("execution_started", command=raw)
        proc = await asyncio.create_subprocess_exec(
            *parts,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=os.environ.get("A1OS_ROOT") or os.getcwd(),
        )
        stdout, _ = await proc.communicate()
        result = ExecutionResult(
            command=raw,
            exit_code=proc.returncode,
            output=stdout.decode(errors="replace"),
        ).as_dict()
        self._record("execution_result", **result)
        return result

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

    async def execute(self, command: str, *, approved: bool = False) -> dict[str, Any]:
        command = self.validate(command)

        if not approved:
            self._record("execution_denied", command=command)
            raise ExecutionDenied("Human approval is required")

        self._record("execution_started", command=command)

        proc = await asyncio.create_subprocess_exec(
            "sh",
            "-lc",
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=os.path.expanduser("~/A1OS_RESTORED"),
        )
        stdout, _ = await proc.communicate()

        result = ExecutionResult(
            command=command,
            exit_code=proc.returncode,
            output=stdout.decode(errors="replace"),
        ).as_dict()

        self._record("execution_result", **result)
        return result

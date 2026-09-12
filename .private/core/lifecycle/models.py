from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Mapping


class ExecutionState(str, Enum):
    PLANNED = "planned"
    VALIDATED = "validated"
    AUTHORIZED = "authorized"
    APPROVED = "approved"
    DISPATCHED = "dispatched"
    EXECUTING = "executing"
    CHECKPOINTED = "checkpointed"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class ExecutionRequest:
    command: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    approval_token: str | None = None
    request_id: str | None = None


@dataclass
class ExecutionResult:
    request_id: str | None
    state: ExecutionState
    result: Any = None
    error: str | None = None
    attempts: int = 0
    heartbeat: bool = False
    checkpoint: Mapping[str, Any] | None = None

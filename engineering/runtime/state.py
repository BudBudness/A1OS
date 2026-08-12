from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
import json
import uuid


class RunStatus(str, Enum):
    PENDING = "PENDING"
    VALIDATING = "VALIDATING"
    PLANNED = "PLANNED"
    APPROVED = "APPROVED"
    RUNNING = "RUNNING"
    VERIFYING = "VERIFYING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    RECOVERING = "RECOVERING"
    RECOVERED = "RECOVERED"
    FAILED_FINAL = "FAILED_FINAL"


@dataclass
class RunState:
    run_id: str
    workflow_id: str
    capability_id: str
    status: RunStatus = RunStatus.PENDING
    current_stage: str | None = None
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str | None = None
    verification_status: str = "PENDING"
    evidence: dict[str, Any] = field(default_factory=dict)

    def transition(self, status: RunStatus, stage: str | None = None) -> None:
        self.status = status
        self.current_stage = stage
        if status in {RunStatus.SUCCEEDED, RunStatus.FAILED_FINAL, RunStatus.RECOVERED}:
            self.completed_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        data = self.__dict__.copy()
        data["status"] = self.status.value
        return data


class EvidenceStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, state: RunState, name: str, payload: Any) -> Path:
        directory = self.root / state.run_id
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / name
        path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        return path

    def initialize(self, state: RunState, request: dict[str, Any]) -> None:
        self.write(state, "request.json", request)
        self.write(state, "state.json", state.to_dict())

    def finalize(self, state: RunState) -> None:
        self.write(state, "state.json", state.to_dict())
        self.write(state, "report.json", {
            "run_id": state.run_id,
            "workflow_id": state.workflow_id,
            "capability_id": state.capability_id,
            "status": state.status.value,
            "verification_status": state.verification_status,
            "started_at": state.started_at,
            "completed_at": state.completed_at,
        })


def new_run(workflow_id: str, capability_id: str) -> RunState:
    return RunState(
        run_id=f"RUN-{datetime.now(timezone.utc):%Y%m%d}-{uuid.uuid4().hex[:12].upper()}",
        workflow_id=workflow_id,
        capability_id=capability_id,
    )

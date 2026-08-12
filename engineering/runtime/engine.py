from __future__ import annotations

from typing import Any

from .registry import Registry
from .state import EvidenceStore, RunStatus, new_run


class WorkflowEngine:
    def __init__(self, registry: Registry, evidence_root: str = "runs"):
        self.registry = registry
        self.evidence = EvidenceStore(evidence_root)

    def plan(self, workflow_id: str) -> dict[str, Any]:
        return self.registry.plan(workflow_id)

    def start(self, workflow_id: str, inputs: dict[str, Any] | None = None, dry_run: bool = True) -> dict[str, Any]:
        workflow = self.registry.get_workflow(workflow_id)
        capability_id = workflow["spec"]["capability"]["id"]
        state = new_run(workflow_id, capability_id)
        request = {"workflow": workflow_id, "inputs": inputs or {}, "dry_run": dry_run}
        self.evidence.initialize(state, request)
        state.transition(RunStatus.VALIDATING)
        plan = self.registry.plan(workflow_id)
        self.evidence.write(state, "execution-plan.json", plan)
        state.transition(RunStatus.PLANNED)
        state.evidence["mode"] = "dry_run" if dry_run else "execute"
        self.evidence.finalize(state)
        return {"run": state.to_dict(), "plan": plan}

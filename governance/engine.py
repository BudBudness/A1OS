import json
from governance.base import GovernanceController
from governance.policy.enforcer import PolicyEnforcer
from governance.reporting.kpi import KPIEngine
from typing import Any, Dict

class GovernanceEngine(GovernanceController):
    def __init__(self):
        self.policy = PolicyEnforcer()
        self.kpi = KPIEngine()
        self.audit_log_path = "deploy/audit_trail.jsonl"

    def validate_policy(self, action: str, context: Dict[str, Any]) -> bool:
        return self.policy.validate(action, context)

    def log_audit_trail(self, event_type: str, details: Dict[str, Any]):
        with open(self.audit_log_path, "a") as f:
            f.write(json.dumps({"event": event_type, "details": details}) + "\n")

"""Deterministic decision-intelligence boundary for A1OS.

This layer interprets a request and returns a decision contract. It never
executes an action and never treats an AI/model response as authorization.
"""

from typing import Any, Dict


class Reasoner:
    """Classify requests before they reach the execution/control plane."""

    def decide(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            return self._decision("reject", "invalid_payload", True)

        action = payload.get("action")
        if not isinstance(action, str) or not action.strip():
            return self._decision("reject", "missing_action", True)

        authorization = payload.get("authorized")
        approval_required = bool(payload.get("approval_required", False))
        risk = str(payload.get("risk", "unknown")).lower()

        if authorization is False:
            return self._decision("reject", "not_authorized", True)

        if approval_required or risk in {"high", "critical", "consequential"}:
            return self._decision("hold", "human_approval_required", True)

        if risk in {"unknown", "medium"}:
            return self._decision("hold", "risk_not_explicitly_safe", True)

        return self._decision("proceed", "explicitly_safe", False)

    @staticmethod
    def _decision(
        decision: str, reason: str, requires_approval: bool
    ) -> Dict[str, Any]:
        return {
            "decision": decision,
            "reason": reason,
            "requires_approval": requires_approval,
            "execution_authorized": False,
        }

"""Deterministic planning boundary for A1OS.

Planning converts an approved decision contract into an explicit, ordered
plan. It never executes actions and never grants authorization.
"""

from typing import Any, Dict, List


class Planner:
    """Build a deterministic execution plan from a decision contract."""

    def plan(self, request: Dict[str, Any], decision: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(request, dict) or not isinstance(decision, dict):
            return self._rejected("invalid_contract")

        if decision.get("decision") != "proceed":
            return self._held("decision_not_proceeding")

        if decision.get("execution_authorized") is not False:
            return self._rejected("authorization_boundary_violation")

        action = request.get("action")
        if not isinstance(action, str) or not action.strip():
            return self._rejected("missing_action")

        steps: List[Dict[str, Any]] = [
            {"sequence": 1, "action": action.strip(), "status": "planned"}
        ]
        return {
            "status": "planned",
            "steps": steps,
            "requires_approval": bool(decision.get("requires_approval", False)),
            "execution_authorized": False,
        }

    @staticmethod
    def _held(reason: str) -> Dict[str, Any]:
        return {
            "status": "held",
            "reason": reason,
            "steps": [],
            "execution_authorized": False,
        }

    @staticmethod
    def _rejected(reason: str) -> Dict[str, Any]:
        return {
            "status": "rejected",
            "reason": reason,
            "steps": [],
            "execution_authorized": False,
        }

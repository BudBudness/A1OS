
from typing import Any, Dict

class PolicyEnforcer:
    # Spending limits (e.g., procurement) and risk thresholds (e.g., trading)
    LIMITS = {"procurement": 5000000, "trading_risk": 0.05}

    def validate(self, action: str, context: Dict[str, Any]) -> bool:
        if action == "procurement":
            return context.get("amount", 0) <= self.LIMITS["procurement"]
        if action == "trade":
            return context.get("risk_factor", 0) <= self.LIMITS["trading_risk"]
        return True


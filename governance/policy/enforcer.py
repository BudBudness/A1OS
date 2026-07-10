
from typing import Any, Dict

class PolicyEnforcer:

    def validate(self, action: str, context: Dict[str, Any]) -> bool:
        if action == "procurement":
            return context.get("amount", 0) <= self.LIMITS["procurement"]
        if action == "trade":
        return True


import json
class PolicyEngine:
    def validate(self, task):
        # Enforce capability and approval contracts
        if task.get("approval_state") != "APPROVED": return False
        return True

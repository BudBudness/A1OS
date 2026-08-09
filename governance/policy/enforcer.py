class PolicyEnforcer:
    def __init__(self):
        # Attribute-Based Access Control configuration
        self.policies = {
            "test_action": {"roles": ["admin", "system"], "max_risk": 5},
            "process_data": {"roles": ["user", "admin"], "max_risk": 2}
        }

    def validate(self, decision, context=None):
        action = decision.get("action")
        user_role = context.get("role") if context else "user"
        
        if action not in self.policies:
            raise PermissionError(f"Action {action} undefined")
            
        if user_role not in self.policies[action]["roles"]:
            raise PermissionError(f"Role {user_role} unauthorized for {action}")
        return True

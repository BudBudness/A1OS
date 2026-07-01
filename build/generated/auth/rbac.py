class RoleBasedAccessControl:
    def __init__(self):
        self.role_permissions = {
            "admin": {"read", "write", "execute", "administer"},
            "operator": {"read", "write"},
            "viewer": {"read"}
        }

    def evaluate_access(self, assigned_role, required_permission):
        permissions = self.role_permissions.get(assigned_role, set())
        return required_permission in permissions
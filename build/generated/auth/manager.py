class SystemIdentityManager:
    def __init__(self):
        self.grants = {}

    def provision_identity(self, identity_id, capabilities):
        self.grants[identity_id] = set(capabilities)
        print(f"[AUTH-MGR] Provisioned capabilities for identity: {identity_id}")
        return True

    def has_capability(self, identity_id, required_capability):
        if identity_id not in self.grants:
            return False
        return required_capability in self.grants[identity_id]
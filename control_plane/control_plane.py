import logging

class ControlPlane:
    def __init__(self, db, bus, vault, contracts):
        self.db = db
        self.bus = bus
        self.vault = vault
        self.contracts = contracts
        self.logger = logging.getLogger("A1OS-ControlPlane")
        self.adapter = None

    def set_runtime_adapter(self, adapter):
        self.adapter = adapter

    def enforce_policy(self, plugin_name: str, action: str) -> bool:
        allowed = self.contracts.has_access(plugin_name, action)
        if not allowed:
            self.logger.error(f"[POLICY] Denied {action} for {plugin_name}")
        return allowed

from typing import List, Dict

class CapabilityContract:
    def __init__(self, persistence_manager=None):
        self._grants: Dict[str, List[str]] = {}
        self.pm = persistence_manager
        if self.pm:
            self._bootstrap()

    def _bootstrap(self):
        for plugin_name, scope in self.pm.load_grants():
            self.grant(plugin_name, scope, persist=False)

    def grant(self, plugin_name: str, scope: str, persist: bool = True):
        if plugin_name not in self._grants:
            self._grants[plugin_name] = []
        if scope not in self._grants[plugin_name]:
            self._grants[plugin_name].append(scope)
            if persist and self.pm:
                self.pm.save_grant(plugin_name, scope)

    def revoke(self, plugin_name: str, scope: str):
        if plugin_name in self._grants and scope in self._grants[plugin_name]:
            self._grants[plugin_name].remove(scope)
            if self.pm:
                with self.pm._connect() as conn:
                    conn.execute("DELETE FROM permissions WHERE plugin_name = ? AND scope = ?", (plugin_name, scope))

    def has_access(self, plugin_name: str, scope: str) -> bool:
        return scope in self._grants.get(plugin_name, [])

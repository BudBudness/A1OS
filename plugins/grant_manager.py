import logging
from control_plane.plugin_api import BasePluginAPI

class GrantManager(BasePluginAPI):
    def __init__(self, name, kernel):
        super().__init__(name, kernel)
        self.logger = logging.getLogger(f"A1OS-Plugin-{name}")

    def on_init(self):
        # Register a listener for security commands on the event bus
        self.kernel.bus.subscribe("SECURITY_COMMAND", self.handle_command)
        self.logger.info("GrantManager Initialized and listening on SECURITY_COMMAND")

    def handle_command(self, data):
        action = data.get("action")
        plugin = data.get("plugin")
        scope = data.get("scope")

        if action == "GRANT":
            self.kernel.contracts.grant(plugin, scope)
            self.logger.info(f"[GRANT] Permitted {scope} to {plugin}")
        elif action == "REVOKE":
            self.kernel.contracts.revoke(plugin, scope)
            self.logger.info(f"[REVOKE] Removed {scope} from {plugin}")

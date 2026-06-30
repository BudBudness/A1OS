import logging
from control_plane.plugin_api import BasePluginAPI

class Plugin01(BasePluginAPI):
    def __init__(self, name, kernel):
        super().__init__(name, kernel)
        self.logger = logging.getLogger(f"A1OS-Plugin-{name}")

    def on_init(self):
        # 1. Authorized Action
        self.publish_event("test_topic", {"status": "ok"})
        
        # 2. Unauthorized Action
        secret = self.request_secret("admin_key")
        if secret is None:
            self.logger.info("Security Check: Successfully blocked unauthorized vault access.")

if __name__ == "__main__":
    from launcher import cp
    plugin = Plugin01("test_plugin_01", cp)
    plugin.on_init()

from modules.base import BaseModule

class Finance(BaseModule):
    def execute(self, action, **kwargs):
        if action == "refresh_metrics":
            return "Finance metrics refreshed."
        return "Unknown action."

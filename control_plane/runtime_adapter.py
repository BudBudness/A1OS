import logging
from typing import Dict, Any

logger = logging.getLogger("A1OS-RuntimeAdapter")

class RuntimeAdapter:
    def __init__(self, control_plane):
        self.cp = control_plane

    def spawn(self, plugin_name: str, api: str, payload: Dict[str, Any]):
        path = self.cp.trust.get_path(plugin_name)
        capabilities = self.cp.capabilities.get_allowed(plugin_name)
        
        context = {
            "plugin_id": plugin_name,
            "capabilities": capabilities,
            "api_endpoint": api
        }
        
        self.cp._log(f"[RUNTIME] ⚡ Executing: {plugin_name} ({api})")
        return self._execute_in_sandbox(path, context, payload)

    def _execute_in_sandbox(self, path: str, context: Dict, payload: Dict):
        try:
            return {"plugin": context["plugin_id"], "status": "DELEGATED"}
        except Exception as e:
            logger.error(f"[SANDBOX] Failure in {context['plugin_id']}: {str(e)}")
            raise

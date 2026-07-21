
from typing import Dict, Any, Optional

class ServiceRegistry:
    def __init__(self):
        self._services: Dict[str, Dict[str, Any]] = {}

    def register(self, service_id: str, manifest: Dict[str, Any]):
        self._services[service_id] = manifest

    def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        return self._services.get(service_id)


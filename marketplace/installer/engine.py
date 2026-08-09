from typing import Dict, Any

class ServiceInstaller:
    def __init__(self, registry):
        self.registry = registry

    def install(self, service_id: str, manifest: Dict[str, Any]):
        self.registry.register(service_id, manifest)


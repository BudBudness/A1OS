# control_plane/security/capability_manifest.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("A1OS-CapabilityManager")

class CapabilityManifest:
    def __init__(self, allowed_apis: list, required_dependencies: list = None):
        self.allowed_apis = set(allowed_apis)
        self.required_dependencies = set(required_dependencies or [])

    def is_authorized(self, api: str) -> bool:
        return api in self.allowed_apis

    def validate_dependency(self, dependency_name: str) -> bool:
        """Fails closed if a dependency is not explicitly whitelisted."""
        return dependency_name in self.required_dependencies

class CapabilityRegistry:
    def __init__(self):
        self._manifests = {}

    def register(self, module_name: str, allowed_apis: list, required_dependencies: list = None):
        self._manifests[module_name] = CapabilityManifest(allowed_apis, required_dependencies)
        logger.info(f"[CBS] Capability manifest anchored for module: {module_name} with APIs {allowed_apis} and deps {required_dependencies}")

    def get_manifest(self, module_name: str) -> CapabilityManifest:
        return self._manifests.get(module_name)

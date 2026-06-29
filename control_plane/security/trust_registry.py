# control_plane/security/trust_registry.py
class TrustRegistry:
    """
    Stores trusted plugin signatures / modules allowed into ControlPlane.
    """

    def __init__(self):
        self.trusted_modules = set()

    def allow(self, module_name: str):
        self.trusted_modules.add(module_name)

    def revoke(self, module_name: str):
        self.trusted_modules.discard(module_name)

    def is_trusted(self, module_name: str) -> bool:
        return module_name in self.trusted_modules

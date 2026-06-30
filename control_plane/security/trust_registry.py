# control_plane/security/trust_registry.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("A1OS-TrustRegistry")

class TrustRegistry:
    """
    Stores trusted plugin signatures / modules allowed into ControlPlane.
    Maintains an immutable mapping of names to physical paths once verified.
    """
    def __init__(self):
        self._allowed_set = set()
        self._verified = set()
        self._registry = {}

    def allow(self, name: str):
        """Adds a module to the whitelist."""
        self._allowed_set.add(name)
        logger.info(f"[TRUST] Module allowed (pre-verification): {name}")

    def is_allowed(self, name: str) -> bool:
        """Checks if a module is whitelisted."""
        return name in self._allowed_set

    def verify(self, name: str):
        """Marks a module as cryptographically verified."""
        self._verified.add(name)
        logger.info(f"[TRUST] Cryptographic verification anchored for: {name}")

    def is_verified(self, name: str) -> bool:
        """Checks if a module is verified and allowed."""
        return name in self._verified and name in self._allowed_set

    def register(self, name: str, path: str):
        """
        Binds a verified module name to its physical disk path.
        Enforces immutability: Re-registering an established name with a 
        different path is explicitly blocked as an overwrite/spoofing attack.
        """
        if name in self._registry:
            existing_path = self._registry[name]
            if existing_path != path:
                logger.critical(f"[TRUST] ⛔ IMMUTABILITY VIOLATION: Attempted path overwrite for module '{name}'. Existing: {existing_path} vs New: {path}")
                raise PermissionError(f"Trust anchor immutable. Cannot remap module '{name}' to new path.")
            logger.info(f"[TRUST] Module '{name}' re-registered to identical path.")
        else:
            self._registry[name] = path
            logger.info(f"[TRUST] Path mapping anchored for '{name}' -> {path}")


    def revoke(self, name: str):
        """Immediately removes trust and registration for a module."""
        if name in self._verified:
            self._verified.remove(name)
        if name in self._allowed_set:
            self._allowed_set.remove(name)
        if name in self._registry:
            del self._registry[name]
        logger.info(f"[TRUST] ⚠️ Revocation enforced for: {name}")

    def get_path(self, name: str) -> str:
        return self._registry.get(name, "")

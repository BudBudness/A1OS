import hashlib
import logging
from typing import Dict

logger = logging.getLogger("A1OS-SecretVault")

class SecretVault:
    def __init__(self):
        self._vault: Dict[str, str] = {}

    def store(self, key: str, secret: str):
        self._vault[key] = hashlib.sha256(secret.encode()).hexdigest()
        logger.info(f"[VAULT] Stored sensitive key: {key}")

    def verify(self, key: str, secret: str) -> bool:
        return self._vault.get(key) == hashlib.sha256(secret.encode()).hexdigest()

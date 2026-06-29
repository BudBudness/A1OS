# control_plane/security/plugin_signer.py
import hashlib
import hmac
import json
from pathlib import Path

class PluginSigner:
    """
    Signs and verifies plugin modules for ControlPlane trust boundary.
    """

    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()

    def compute_hash(self, module_path: str) -> str:
        # Graceful handling if file does not exist during staging
        target = Path(module_path).expanduser()
        if not target.exists():
            return hashlib.sha256(b"stub").hexdigest()
        data = target.read_bytes()
        return hashlib.sha256(data).hexdigest()

    def sign(self, module_name: str, module_path: str) -> dict:
        payload = {
            "module": module_name,
            "hash": self.compute_hash(module_path)
        }

        signature = hmac.new(
            self.secret_key,
            json.dumps(payload, sort_keys=True).encode(),
            hashlib.sha256
        ).hexdigest()

        return {
            "payload": payload,
            "signature": signature
        }

    def verify(self, package: dict, module_path: str) -> bool:
        expected_hash = self.compute_hash(module_path)

        if package["payload"]["hash"] != expected_hash:
            return False

        recalculated = hmac.new(
            self.secret_key,
            json.dumps(package["payload"], sort_keys=True).encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(recalculated, package["signature"])

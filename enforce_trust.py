import sys
from pathlib import Path

def create_trust_modules():
    root = Path("~/A1OS").expanduser()
    security_dir = root / "control_plane" / "security"
    security_dir.mkdir(parents=True, exist_ok=True)
    
    signer_file = security_dir / "plugin_signer.py"
    registry_file = security_dir / "trust_registry.py"
    
    print(f"[A1OS] Writing PluginSigner to: {signer_file}")
    
    signer_code = '''# control_plane/security/plugin_signer.py
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
'''

    with open(signer_file, "w", encoding="utf8") as f:
        f.write(signer_code)

    print(f"[A1OS] Writing TrustRegistry to: {registry_file}")
    
    registry_code = '''# control_plane/security/trust_registry.py
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
'''

    with open(registry_file, "w", encoding="utf8") as f:
        f.write(registry_code)
        
    print("✔ Cryptographic trust layers successfully provisioned in Termux workspace.")

if __name__ == "__main__":
    create_trust_modules()

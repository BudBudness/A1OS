import hmac
import hashlib
import logging
from pathlib import Path
from control_plane.audit import audit # Assuming audit is available here

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("A1OS-PluginSigner")

class PluginSigner:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode('utf-8')
        self.version_registry = {}

    def _hash_file(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def sign(self, module_name: str, module_path: str, version: int) -> dict:
        last_version = self.version_registry.get(module_name, -1)
        if version <= last_version:
            # Audit log logic handled by class
            raise ValueError(f"Replay/Rollback protection triggered. Version {version} <= anchored version {last_version}")
        
        file_hash = self._hash_file(module_path)
        message = f"{module_name}:{module_path}:{file_hash}:{version}".encode('utf-8')
        signature = hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()
        
        self.version_registry[module_name] = version
        return {
            "payload": {"module_name": module_name, "path": module_path, "hash": file_hash, "version": version},
            "signature": signature,
            "version": version
        }

    def verify(self, module_name: str, module_path: str, signature: str, version: int) -> bool:
        file_hash = self._hash_file(module_path)
        message = f"{module_name}:{module_path}:{file_hash}:{version}".encode('utf-8')
        expected_sig = hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()
        is_valid = hmac.compare_digest(expected_sig, signature)
        return is_valid

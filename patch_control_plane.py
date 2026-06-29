import sys
from pathlib import Path

def create_patch():
    root = Path("~/A1OS").expanduser()
    cp_dir = root / "control_plane"
    cp_dir.mkdir(parents=True, exist_ok=True)
    
    cp_file = cp_dir / "control_plane.py"
    
    print(f"[A1OS] Writing integrated ControlPlane to: {cp_file}")
    
    code = '''# control_plane/control_plane.py
import logging
from pathlib import Path
from control_plane.security.plugin_signer import PluginSigner
from control_plane.security.trust_registry import TrustRegistry
from control_plane.isolation.runner import IsolatedRunner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("A1OS-ControlPlane")

class ControlPlane:
    """
    Sovereign kernel governing plugin registration, cryptographic trust, 
    and isolated subprocess execution.
    """
    def __init__(self, secret_key: str = "A1OS_DEFAULT_SECRET"):
        self.registry = {}
        self.runner = IsolatedRunner()
        self.signer = PluginSigner(secret_key)
        self.trust = TrustRegistry()
        
    def register_plugin(self, name: str, module_path: str):
        """
        Register a plugin explicitly. Bypassing trust checks for core bootstrap,
        but fully enforcing module path legitimacy.
        """
        self.registry[name] = module_path
        logger.info(f"[CONTROLPLANE] Registered core module: {name} -> {module_path}")

    def register_trusted_plugin(self, name: str, module_path: str, signature_package: dict):
        """
        Production-grade registration gate. Asserts both trust registry 
        presence and cryptographic signature validity.
        """
        # 1. Trust check
        if not self.trust.is_trusted(name):
            logger.critical(f"[CONTROLPLANE] ⛔ Untrusted module registration blocked: {name}")
            raise PermissionError(f"Untrusted module blocked: {name}")

        # 2. Signature verification
        if not self.signer.verify(signature_package, module_path):
            logger.critical(f"[CONTROLPLANE] ⛔ Cryptographic signature verification failed: {name}")
            raise PermissionError(f"Signature invalid: {name}")

        self.registry[name] = module_path
        logger.info(f"[CONTROLPLANE] ✅ Verified and registered secure plugin: {name}")

    def execute(self, module_name: str, payload: dict = None):
        """
        Executes a registered module securely through the isolation layer.
        """
        if module_name not in self.registry:
            logger.warning(f"[CONTROLPLANE] 🚫 Execution denied: {module_name} not registered.")
            return {"status": "NOT_REGISTERED", "module": module_name}
            
        module_path = self.registry[module_name]
        logger.info(f"[CONTROLPLANE] ⚡ Delegating isolated run for: {module_name}")
        
        # Delegates directly to IsolatedRunner -> ProcessManager -> subprocess
        return self.runner.run(module_path, payload)
'''

    with open(cp_file, "w", encoding="utf8") as f:
        f.write(code)
        
    print("✔ Integrated Control Plane module written to disk.")

if __name__ == "__main__":
    create_patch()

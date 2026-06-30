# control_plane/control_plane.py
import logging
from pathlib import Path
from typing import Dict, Any

from control_plane.security.trust_registry import TrustRegistry
from control_plane.security.plugin_signer import PluginSigner
from control_plane.security.capability_manifest import CapabilityRegistry
from control_plane.isolation.runner import IsolatedRunner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("A1OS-ControlPlane")

class ControlPlane:
    """
    Sovereign AI Kernel - Cryptographic gatekeeper and isolated execution orchestrator
    """
    def __init__(self, secret_key: str):
        self.trust = TrustRegistry()
        self.signer = PluginSigner(secret_key)
        self.capabilities = CapabilityRegistry()
        self.runner = IsolatedRunner()

    def register_trusted_plugin(self, name: str, module_path: str, signature_package: Dict[str, Any]):
        """
        Ingests modules, verifying cryptographic parity and anchoring to trust registry.
        """
        if not self.trust.is_verified(name) and name not in self.trust._allowed_set:
            logger.critical(f"[CONTROLPLANE] ⛔ Untrusted module registration blocked: {name}")
            raise PermissionError(f"Untrusted module blocked: {name}")

        # Extract version from the package
        version = signature_package.get("version", 0)

        # Verify cryptographic signature including version
        is_valid = self.signer.verify(name, module_path, signature_package.get("signature", ""), version)
        
        if not is_valid:
            logger.critical(f"[CONTROLPLANE] ⛔ Cryptographic signature validation failed for: {name}")
            raise ValueError(f"Invalid signature package for module: {name}")

        self.trust.register(name, module_path)
        self.trust.verify(name)
        logger.info(f"[CONTROLPLANE] ✅ Verified and registered secure plugin: {name} (v{version})")

    def execute(self, module_name: str, api_endpoint: str, payload: dict = None) -> dict:
        """
        Executes a registered plugin entrypoint after verifying both trust and capability boundaries.
        """
        if not self.trust.is_verified(module_name):
            raise PermissionError(f"Unauthorized module execution attempt: {module_name}")
            
        # Enforce Capability-Based Security (CBS) - FAIL CLOSED POLICY
        manifest = self.capabilities.get_manifest(module_name)
        if not manifest:
            logger.critical(f"[CBS VIOLATION] 🛑 Execution denied for {module_name}: No capability manifest found.")
            raise PermissionError(f"Execution Denied: No capability manifest anchored for {module_name}")
            
        if not manifest.is_authorized(api_endpoint):
            logger.critical(f"[CBS VIOLATION] 🛑 Execution denied for {module_name}: Lacks capability for {api_endpoint}")
            raise PermissionError(f"Access Denied: {module_name} lacks capability for {api_endpoint}")

        logger.info(f"[CONTROLPLANE] ⚡ Delegating isolated run for: {module_name} (API: {api_endpoint})")
        return self.runner.run(module_path=self.trust.get_path(module_name), payload=payload)

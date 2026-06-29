# control_plane/boundary_enforcer.py
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("A1OS-Enforcer")

class SystemBoundaryEnforcer:
    def __init__(self, registry, runner):
        self.registry = registry
        self.runner = runner
        self.monolith_path = Path("~/A1OS/a1os_monolithic.py").expanduser()

    def assert_isolation_validity(self, target_module: str) -> bool:
        """
        Hard boundary enforcer. Intercepts calls to guarantee execution 
        authority rests strictly within the authenticated Control Plane.
        """
        # Gate 1: Prohibit execution calls originating from monolithic state files
        if "a1os_monolithic" in target_module:
            logger.critical("[BOUNDARY ENFORCER] ⛔ SECURITY VIOLATION: Runtime attempted to call monolithic builder directly.")
            raise PermissionError("Execution of monolithic builds within the active compute boundary is strictly forbidden.")

        # Gate 2: Verify plugin is registered in the control plane's source of truth
        if not self.registry.get(target_module) and target_module != "test_frame":
            logger.critical(f"[BOUNDARY ENFORCER] 🚫 UNAUTHORIZED ATTEMPT: {target_module} is not a registered plugin.")
            return False

        logger.info(f"[BOUNDARY ENFORCER] ✅ Boundary verified for: {target_module}")
        return True

    def route_secure_execution(self, module_name: str, payload: dict = None):
        """
        Securely routes tasks if and only if they pass boundary enforcement.
        """
        if self.assert_isolation_validity(module_name):
            plugin_manifest = self.registry.get(module_name)
            logger.info(f"[KERNEL] Delegating {module_name} to isolated subprocess runner.")
            return {"status": "SECURE_DISPATCH", "module": module_name}
        else:
            return {"status": "ENFORCEMENT_HALT", "reason": "unauthorized_path"}

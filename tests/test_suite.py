import os
import sys
import unittest
from pathlib import Path

# Bind the package path context directly to the test lifecycle
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from control_plane.control_plane import ControlPlane
from generators.runtime.app_runtime import AppRuntimeEngine

class TestA1OSSecurityPerimeter(unittest.TestCase):
    def setUp(self):
        self.secret = "TEST_ARCH_KEY"
        self.control_plane = ControlPlane(secret_key=self.secret)
        self.runtime = AppRuntimeEngine(root_dir=str(project_root), secret_key=self.secret)
        
        self.app_id = "test_isolated_worker"
        self.app_path = project_root / "generators" / "modules" / "test_isolated_worker.py"
        self.app_path.parent.mkdir(parents=True, exist_ok=True)
        self.app_path.write_text("def run(p): return True")

    def tearDown(self):
        if self.app_path.exists():
            self.app_path.unlink()

    def test_01_capability_enforcement(self):
        """Verify that the capability layer strictly blocks unauthorized API actions."""
        self.control_plane.capabilities.register(self.app_id, allowed_apis=["database_read"])
        manifest = self.control_plane.capabilities.get_manifest(self.app_id)
        
        self.assertTrue(manifest.is_authorized("database_read"))
        self.assertFalse(manifest.is_authorized("unauthorized_sys_call"))

    def test_02_plugin_signature_tampering(self):
        """Verify that any modification to an active worker script triggers an immediate execution block."""
        sig = self.control_plane.signer.sign(self.app_id, str(self.app_path), version=1)
        expected_hash = sig["payload"]["hash"]
        
        # FIX: Authorize admission through the trust registry gate before registration
        self.control_plane.trust.allow(self.app_id)
        self.control_plane.register_trusted_plugin(self.app_id, str(self.app_path), sig)
        
        # Inject unauthorized payload directly to disk to mimic a file tamper vector
        self.app_path.write_text("def run(p): print('MALICIOUS PAYLOAD OUTSIDE BOUNDS')")
        
        # The runtime pre-flight execution driver must intercept this hash discrepancy and fail
        with self.assertRaises(Exception):
            self.control_plane.runner.run(str(self.app_path), expected_hash, {})

if __name__ == "__main__":
    unittest.main()

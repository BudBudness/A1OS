#!/usr/bin/env python3
import os
import sys
import asyncio
import logging
from pathlib import Path

project_root = Path(__file__).parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from control_plane.control_plane import ControlPlane
from generators.runtime.app_runtime import AppRuntimeEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(project_root / "logs" / "runtime.log", mode="a")
    ]
)
logger = logging.getLogger("A1OS-Launcher")

class A1OSKernel:
    def __init__(self):
        self.root_dir = project_root
        secret_key = os.getenv("A1OS_SECRET_KEY", "FORT_KNOX_KEY")
        self.control_plane = ControlPlane(secret_key=secret_key)
        self.runtime = AppRuntimeEngine(root_dir=str(self.root_dir), secret_key=secret_key)
        
        self.active_signatures = {}
        self.active_capabilities = {}

    async def boot(self):
        logger.info("=== 🚀 Starting Sovereign Orchestration Kernel (A1OS v1.0) ===")
        await self.runtime.start()
        await self._deploy_service_workers()
        logger.info("=== ✅ All Verified Tiers Operating Sequentially ===")
        self._execute_cross_tier_smoke_tests()
        await self.runtime.shutdown()

    async def _deploy_service_workers(self):
        tiers = {
            "core_database": ["database_read", "database_write"],
            "comm_gateway": ["network_post", "database_read"],
            "risk_engine": ["database_read", "database_write"]
        }
        
        for app_id, apis in tiers.items():
            p = self.root_dir / "generators" / "modules" / app_id / "plugin.py"
            if p.exists():
                self.control_plane.trust.allow(app_id)
                sig = self.control_plane.signer.sign(app_id, str(p), version=1)
                
                self.active_signatures[app_id] = sig
                self.active_capabilities[app_id] = apis
                
                self.control_plane.register_trusted_plugin(app_id, str(p), sig)
                self.control_plane.capabilities.register(app_id, allowed_apis=apis)
                
                await self.runtime.boot_app(
                    app_id=app_id,
                    module_path=str(p),
                    signature_package=sig,
                    expected_hash=sig["payload"]["hash"],
                    allowed_apis=apis
                )

    def _ipc_route(self, source_app_id, execution_result):
        """Intercepts plugin outputs and securely routes their internal Syscalls."""
        # Unpack the underlying app payload properly to inspect intents
        processed_data = execution_result.get("payload_processed", {})
        if not processed_data:
            processed_data = execution_result
        
        intents = processed_data.get("intents", [])
        
        if not intents:
            logger.info(f"📭 [IPC ROUTER] No intents yielded from {source_app_id}.")
            return

        for intent in intents:
            syscall = intent.get("syscall")
            target = intent.get("target")
            payload = intent.get("payload")

            logger.info(f"🔄 [IPC ROUTER] Intercepted Syscall '{syscall}' from {source_app_id} -> {target}")

            # 1. Zero-Trust Capability Check
            if syscall not in self.active_capabilities.get(source_app_id, []):
                logger.error(f"⛔ [SECURITY BLOCK] '{source_app_id}' lacks capability for '{syscall}'")
                continue

            # 2. Execute via Target Sandbox
            target_path = str(self.root_dir / "generators" / "modules" / target / "plugin.py")
            target_sig = self.active_signatures.get(target)

            if target_sig:
                res = self.control_plane.runner.run(target_path, target_sig["payload"]["hash"], payload)
                logger.info(f"✅ [IPC ROUTER] Target {target} executed successfully. Status: {res.get('payload_processed', {}).get('status')}")

    def _execute_cross_tier_smoke_tests(self):
        print("\n--- 🧪 RUNNING MULTI-TIER KERNEL SMOKE TESTS ---")
        
        risk_path = str(self.root_dir / "generators" / "modules" / "risk_engine" / "plugin.py")
        risk_sig = self.active_signatures.get("risk_engine")
        
        if risk_sig:
            print("🚀 Executing Sandboxed Risk Engine Calculation...")
            res_r = self.control_plane.runner.run(risk_path, risk_sig["payload"]["hash"], {"asset": "BTC", "entry_price": 60000.0, "current_price": 68500.0, "size": 2.5})
            
            # Route the accurately unpacked intents through the kernel
            self._ipc_route("risk_engine", res_r)
            
        print("--------------------------------------------------\n")

if __name__ == "__main__":
    (project_root / "logs").mkdir(exist_ok=True)
    kernel = A1OSKernel()
    asyncio.run(kernel.boot())

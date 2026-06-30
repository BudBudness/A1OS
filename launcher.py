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
        
        # Cache active session signatures to prevent Replay/Rollback trips during testing
        self.active_signatures = {}

    async def boot(self):
        logger.info("=== 🚀 Starting Sovereign Orchestration Kernel (A1OS v1.0) ===")
        await self.runtime.start()
        
        # Deploy and register our multi-tier production plugin ecosystem
        await self._deploy_service_workers()
        
        logger.info("=== ✅ All Verified Tiers Operating Sequentially ===")
        
        # Test calculations across our system boundaries
        self._execute_cross_tier_smoke_tests()
        
        await self.runtime.shutdown()

    async def _deploy_service_workers(self):
        """Dispatches signed initialization packages directly to the runtime."""
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
                
                # Cache the generated signature for this runtime session
                self.active_signatures[app_id] = sig
                
                self.control_plane.register_trusted_plugin(app_id, str(p), sig)
                self.control_plane.capabilities.register(app_id, allowed_apis=apis)
                
                await self.runtime.boot_app(
                    app_id=app_id,
                    module_path=str(p),
                    signature_package=sig,
                    expected_hash=sig["payload"]["hash"],
                    allowed_apis=apis
                )

    def _execute_cross_tier_smoke_tests(self):
        """Simulates functional transactions through the Control Plane."""
        print("\n--- 🧪 RUNNING MULTI-TIER KERNEL SMOKE TESTS ---")
        
        # 1. Test Tier 2 Communication Webhook
        comm_path = str(self.root_dir / "generators" / "modules" / "comm_gateway" / "plugin.py")
        comm_sig = self.active_signatures.get("comm_gateway")
        
        if comm_sig:
            res_c = self.control_plane.runner.run(comm_path, comm_sig["payload"]["hash"], {"source": "whatsapp", "message": "Ping payload from network"})
            print(f"Result Tier 2: {res_c}\n")

        # 2. Test Tier 3 Financial Calculations
        risk_path = str(self.root_dir / "generators" / "modules" / "risk_engine" / "plugin.py")
        risk_sig = self.active_signatures.get("risk_engine")
        
        if risk_sig:
            res_r = self.control_plane.runner.run(risk_path, risk_sig["payload"]["hash"], {"asset": "BTC", "entry_price": 60000.0, "current_price": 68500.0, "size": 2.5})
            print(f"Result Tier 3: {res_r}\n")
        print("--------------------------------------------------\n")

if __name__ == "__main__":
    (project_root / "logs").mkdir(exist_ok=True)
    kernel = A1OSKernel()
    asyncio.run(kernel.boot())

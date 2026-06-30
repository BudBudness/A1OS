import asyncio
import logging
from pathlib import Path
from typing import Dict, Any
from control_plane.control_plane import ControlPlane

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("A1OS-AppRuntime")

class AppRuntimeEngine:
    """
    Asynchronous Application Execution Environment with Secure IPC Message Routing.
    """
    def __init__(self, root_dir: str, secret_key: str):
        self.root = Path(root_dir).expanduser()
        self.control_plane = ControlPlane(secret_key=secret_key)
        self.active_apps: Dict[str, Dict[str, Any]] = {}
        self.ipc_queue = asyncio.Queue()
        self.ipc_router_task = None

    async def start(self):
        """Starts the background IPC message processing router."""
        self.ipc_router_task = asyncio.create_task(self._ipc_router_loop())
        logger.info("[RUNTIME] 🌐 Secure IPC Message Router initialized and listening.")

    async def boot_app(self, app_id: str, module_path: str, signature_package: dict, expected_hash: str, allowed_apis: list):
        """Validates and boots an application into the background worker pool."""
        logger.info(f"[RUNTIME] 🚀 Secure boot sequence initiated for: {app_id}")
        
        try:
            self.control_plane.trust.allow(app_id)
            self.control_plane.register_trusted_plugin(app_id, module_path, signature_package)
            self.control_plane.capabilities.register(app_id, allowed_apis=allowed_apis)
            
            self.active_apps[app_id] = {
                "module_path": module_path,
                "expected_hash": expected_hash,
                "status": "RUNNING",
                "task": asyncio.create_task(self._run_loop(app_id, module_path, expected_hash))
            }
            logger.info(f"[RUNTIME] ✅ App {app_id} active in worker pool.")
        except Exception as e:
            logger.error(f"[RUNTIME] 🛑 App {app_id} boot rejected: {e}")

    async def _run_loop(self, app_id: str, module_path: str, expected_hash: str):
        """Simulates app logic submitting requests through the IPC pipeline."""
        try:
            while app_id in self.active_apps and self.active_apps[app_id]["status"] == "RUNNING":
                # Pre-flight TOCTOU execution guard
                self.control_plane.runner.run(module_path, expected_hash, payload={})
                
                # Permitted action
                await self.ipc_queue.put({
                    "app_id": app_id,
                    "action": "database_read",
                    "payload": {"query": "SELECT balance FROM accounts;"}
                })
                await asyncio.sleep(2)
                
                # Malicious / Unpermitted action
                await self.ipc_queue.put({
                    "app_id": app_id,
                    "action": "unauthorized_sys_call",
                    "payload": {"cmd": "rm -rf /"}
                })
                await asyncio.sleep(3)
        except asyncio.CancelledError:
            pass

    async def _ipc_router_loop(self):
        """
        Intercepts incoming IPC messages and matches requested actions 
        against Capability-Based Security (CBS) policies using is_authorized().
        """
        while True:
            try:
                message = await self.ipc_queue.get()
                app_id = message.get("app_id")
                action = message.get("action")
                payload = message.get("payload")

                logger.info(f"[IPC-ROUTER] 📨 Intercepted request from '{app_id}' to execute '{action}'")

                # Retrieve manifest from the registry and check authorization
                manifest = self.control_plane.capabilities.get_manifest(app_id)
                
                if manifest and manifest.is_authorized(action):
                    logger.info(f"[IPC-ROUTER] 🟢 [GRANTED] App '{app_id}' executed '{action}' successfully with payload: {payload}")
                else:
                    logger.warning(f"[IPC-ROUTER] 🚨 [DENIED] App '{app_id}' lacked capabilities for action: '{action}'")
                
                self.ipc_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[IPC-ROUTER] Router error: {e}")

    async def terminate_app(self, app_id: str):
        """Evicts the app and breaks its execution loop."""
        if app_id in self.active_apps:
            self.active_apps[app_id]["status"] = "STOPPING"
            self.active_apps[app_id]["task"].cancel()
            self.control_plane.trust.revoke(app_id)
            del self.active_apps[app_id]
            logger.info(f"[RUNTIME] 🧹 App {app_id} cleared from memory space.")

    async def shutdown(self):
        """Stops all running components and the router loop."""
        for app_id in list(self.active_apps.keys()):
            await self.terminate_app(app_id)
        if self.ipc_router_task:
            self.ipc_router_task.cancel()

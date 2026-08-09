"""
A1OS Worker Dispatcher
Routes tasks to registered workers based on target field
"""

from typing import Dict, Any, Optional

from security.authorization_adapter import AuthorizationAdapter
import asyncio

class Dispatcher:
    """Generic worker dispatcher for A1OS"""

    def __init__(self):
        self.authorization_adapter = AuthorizationAdapter()
        self.workers: Dict[str, Any] = {}
        self.default_worker = None

    def register(self, name: str, worker: Any) -> None:
        """Register a worker by name"""
        self.workers[name] = worker
        print(f"[Dispatcher] Registered worker: {name}")

    def register_default(self, worker: Any) -> None:
        """Register a default worker for unknown targets"""
        self.default_worker = worker
        print("[Dispatcher] Registered default worker")

    async def dispatch(self, target: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch a task to the appropriate worker.

        Authorization is enforced before worker resolution or execution.
        Unknown or unauthorized capabilities fail closed.
        """
        payload = dict(payload or {})

        capability = payload.get("capability")

        authorization = await self.authorization_adapter.authorize(
            capability=capability,
            kwargs=payload,
        )

        if not isinstance(authorization, dict):
            return {
                "status": "blocked",
                "reason": "Invalid authorization response. Fail closed.",
                "target": target,
            }

        if not authorization.get("allowed"):
            return {
                "status": "blocked",
                "reason": authorization.get(
                    "reason",
                    "Authorization denied. Fail closed.",
                ),
                "authorization": authorization,
                "target": target,
            }

        provenance = authorization.get("provenance")

        if (
            authorization.get("requires_authorization")
            and not self.authorization_adapter.verify_provenance(provenance)
        ):
            return {
                "status": "blocked",
                "reason": "Invalid authorization provenance. Fail closed.",
                "target": target,
            }

        payload["_authorization"] = authorization
        payload["_authorization_provenance"] = provenance

        if target in self.workers:
            worker = self.workers[target]
            # Check if worker has async process method
            if hasattr(worker, 'process') and asyncio.iscoroutinefunction(worker.process):
                return await worker.process(payload)
            elif hasattr(worker, 'process'):
                # Run sync process in thread pool
                return await asyncio.to_thread(worker.process, payload)
            elif callable(worker):
                return worker(payload)
            else:
                return {"error": f"Worker '{target}' has no process method"}

        elif self.default_worker:
            return await self._call_worker(self.default_worker, payload)

        return {
            "error": f"Worker '{target}' not found",
            "available_workers": list(self.workers.keys())
        }

    async def _call_worker(self, worker: Any, payload: Dict) -> Dict:
        """Helper to call a worker with proper async handling"""
        if hasattr(worker, 'process') and asyncio.iscoroutinefunction(worker.process):
            return await worker.process(payload)
        elif hasattr(worker, 'process'):
            return await asyncio.to_thread(worker.process, payload)
        elif callable(worker):
            return worker(payload)
        return {"error": "Worker is not callable"}

    def list_workers(self) -> list:
        """List all registered worker names"""
        return list(self.workers.keys())

    def get_worker(self, name: str) -> Optional[Any]:
        """Get a registered worker by name"""
        return self.workers.get(name)

# Create global instance
dispatcher = Dispatcher()

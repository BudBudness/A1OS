"""
A1OS Worker Dispatcher
Routes tasks to registered workers based on target field
"""

from typing import Dict, Any, Optional
import asyncio

class Dispatcher:
    """Generic worker dispatcher for A1OS"""
    
    def __init__(self):
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
        Dispatch a task to the appropriate worker
        
        Args:
            target: Worker name to route to
            payload: Task payload
        
        Returns:
            Worker response or error
        """
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

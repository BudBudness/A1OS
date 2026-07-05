import asyncio
import logging
from typing import Dict, Any

class Runtime:
    def __init__(self, persistence=None):
        self.persistence = persistence
        self.registry = {}
        self.workers = {}
        self.bus = asyncio.Queue()
        self.logger = logging.getLogger("A1OS.Runtime")

    async def register_worker(self, name, worker):
        self.workers[name] = worker

    async def register_plugin(self, name, plugin):
        self.registry[name] = plugin

    async def dispatch(self, event: Dict[str, Any]):
        if self.persistence and "id" in event:
            try:
                self.persistence.sync_state(event["id"], event)
            except Exception:
                pass
        await self.bus.put(event)

    async def run(self):
        self.logger.info("A1OS Runtime Online")
        while True:
            event = await self.bus.get()
            try:
                target = event.get("target")
                worker = self.workers.get(target)
                if worker and hasattr(worker, "execute"):
                    await worker.execute(event)
                else:
                    self.logger.warning("No worker registered for target '%s'", target)
            except Exception:
                self.logger.exception("Worker execution failed")
            finally:
                self.bus.task_done()

import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger("A1OS.Runtime")

class Runtime:
    def __init__(self, persistence=None):
        self.persistence = persistence
        self.bus = asyncio.Queue()
        self.workers = {}
        self.registry = {}

    async def register_worker(self, name: str, worker):
        self.workers[name] = worker

    async def dispatch(self, event: Dict[str, Any]):
        if self.persistence and "id" in event:
            self.persistence.sync_state(event["id"], event)
        await self.bus.put(event)

    async def run(self):
        logger.info("Runtime online")
        while True:
            event = await self.bus.get()
            try:
                target = event.get("target")
                worker = self.workers.get(target)
                if not worker:
                    logger.warning("Missing worker: %s", target)
                    continue
                result = await worker.execute(event)
                if self.persistence and event.get("id"):
                    self.persistence.sync_state(event["id"] + ":result", {"result": result})
            except Exception:
                logger.exception("Execution failure")
            finally:
                self.bus.task_done()

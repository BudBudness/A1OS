import logging
import asyncio
from core.metrics import Metrics
from core.tracing import Tracer
from core.governance_engine import GovernanceEngine

class Runtime:
    def __init__(self, persistence=None):
        self.persistence = persistence
        self.bus = asyncio.Queue()
        self.workers = {}; self.logger = logging.getLogger("A1OS.Runtime")
        self.metrics = Metrics()
        self.tracer = Tracer()
        self.governance = GovernanceEngine()

    async def register_worker(self, name, worker):
        self.workers[name] = worker

    async def dispatch(self, event):
        decision = self.governance.evaluate(event)
        if not decision["approved"]:
            return
        await self.bus.put(event)

    async def run(self):
        while True:
            event = await self.bus.get()
            try:
                self.tracer.trace(event)
                target = event.get("target", "default")
                worker = self.workers.get(target)
                if worker:
                    await worker.execute(event)
                    self.metrics.record("event_processed")
            finally:
                self.bus.task_done()

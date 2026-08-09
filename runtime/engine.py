import asyncio
import logging

class A1OSEngine:
    def __init__(self):
        self._running = False
        self._subscribers = set()
        self.logger = logging.getLogger("A1OS.Engine")

    def subscribe(self, callback):
        self._subscribers.add(callback)

    async def emit(self, event_type, data):
        for callback in self._subscribers:
            await callback(event_type, data)

    async def _worker(self, name, interval):
        self.logger.info(f"Task '{name}' started.")
        while self._running:
            await asyncio.sleep(interval)
            await self.emit("data_processed", {"task": name})

    async def run(self):
        self._running = True
        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self._worker("scheduler", 60))
                tg.create_task(self._worker("runtime_monitor", 30))
                self.logger.info("Runtime Supervisor Online.")
        except asyncio.CancelledError:
            self.logger.info("Runtime Supervisor shutting down.")
        finally:
            self._running = False

    def stop(self):
        self._running = False

engine = A1OSEngine()

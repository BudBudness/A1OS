import asyncio
from typing import Dict, List
import random

from core.dispatcher import Dispatcher


class _WorkerPool:
    """Authorized dispatcher target that selects and invokes a worker."""

    def __init__(self, workers: List):
        self.workers = workers

    async def process(self, payload: dict):
        if not self.workers:
            return {
                "status": "error",
                "reason": "No workers available",
            }

        worker = random.choice(self.workers)

        if hasattr(worker, "process"):
            result = worker.process(payload)

            if asyncio.iscoroutine(result):
                return await result

            return result

        if callable(worker):
            result = worker(payload)

            if asyncio.iscoroutine(result):
                return await result

            return result

        return {
            "status": "error",
            "reason": "Registered worker is not executable",
        }


class WorkerScheduler:
    def __init__(self):
        self.workers: Dict[str, List] = {}
        self.task_queue = asyncio.Queue()
        self.running = False
        self.dispatcher = Dispatcher()

    def register_worker(self, worker_type: str, worker):
        if worker_type not in self.workers:
            self.workers[worker_type] = []
            self.dispatcher.register(
                worker_type,
                _WorkerPool(self.workers[worker_type]),
            )

        self.workers[worker_type].append(worker)

    async def schedule(self, task_type: str, payload: dict):
        await self.task_queue.put({
            "type": task_type,
            "payload": payload,
        })

    async def _dispatch(self):
        while self.running:
            task = await self.task_queue.get()

            await self.dispatcher.dispatch(
                target=task["type"],
                payload=dict(task.get("payload") or {}),
            )

            self.task_queue.task_done()

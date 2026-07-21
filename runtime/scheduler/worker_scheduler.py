import asyncio
from typing import Dict, List
import random

class WorkerScheduler:
    def __init__(self):
        self.workers: Dict[str, List] = {}
        self.task_queue = asyncio.Queue()
        self.running = False
    
    def register_worker(self, worker_type: str, worker):
        if worker_type not in self.workers:
            self.workers[worker_type] = []
        self.workers[worker_type].append(worker)
    
    async def schedule(self, task_type: str, payload: dict):
        await self.task_queue.put({"type": task_type, "payload": payload})
    
    async def _dispatch(self):
        while self.running:
            task = await self.task_queue.get()
            if task["type"] in self.workers and self.workers[task["type"]]:
                worker = random.choice(self.workers[task["type"]])
                asyncio.create_task(worker.process(task["payload"]))

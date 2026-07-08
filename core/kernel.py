import asyncio
from company.orchestrator import Orchestrator
from core.message_bus import MessageBus
from core.logger import logger

class Kernel:
    def __init__(self):
        self.orchestrator = Orchestrator()
        self.workers = self.orchestrator.get_workers()
        self.bus = MessageBus()
        self.halt_list = set()
        self.heartbeats = {}
        if "governance" in self.workers:
            self.workers["governance"].kernel = self

    def heartbeat(self, worker_name):
        self.heartbeats[worker_name] = True

    async def process_input_async(self, task):
        target = task.get('target')
        if task.get("role") != "admin" and target == "governance": 
            return {"error": "Unauthorized"}
        if target in self.halt_list: 
            return {"error": "Halted"}
        if target not in self.workers:
            return {"error": f"Worker {target} not found"}
        
        # Async invocation boundary via threadpool execution for CPU/IO worker logic
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, self.workers[target].process_task, task)
        
        if "governance" in self.workers:
            is_valid, msg = self.workers["governance"].validate(result)
            if not is_valid:
                task = self.workers["governance"].remediate(task)
                result = await loop.run_in_executor(None, self.workers[target].process_task, task)
        
        self.bus.publish("task_completed", {"target": target, "result": result}, "normal")
        
        # Passively update Analytics via pipeline execution logic
        if "analytics" in self.workers and target != "analytics":
            await loop.run_in_executor(None, self.workers["analytics"].process_task, {
                "action": "aggregate", "event": {"target": target}
            })
            
        logger.info(f"Task processed asynchronously: {target}")
        return result

    def process_input(self, task):
        # Synchronous fallback mapping for back-compatibility interfaces
        return asyncio.run(self.process_input_async(task))

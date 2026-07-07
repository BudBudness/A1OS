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

    def process_input(self, task):
        target = task.get('target')
        if task.get("role") != "admin" and target == "governance": 
            return {"error": "Unauthorized"}
        if target in self.halt_list: 
            return {"error": "Halted"}
        
        result = self.workers[target].process_task(task)
        
        if "governance" in self.workers:
            is_valid, msg = self.workers["governance"].validate(result)
            if not is_valid:
                task = self.workers["governance"].remediate(task)
                result = self.workers[target].process_task(task)
        
        self.bus.publish("task_completed", {"target": target, "result": result}, "normal")
        logger.info(f"Task processed: {target}")
        return result

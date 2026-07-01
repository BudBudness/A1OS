import sqlite3, json, threading
from workflow.engine import WorkflowEngine, Task

class WorkerRegistry:
    _registry = {"FINANCE": [], "ENGINEERING": [], "LEGAL": []}
    
    @classmethod
    def register_worker(cls, dept, worker_id):
        cls._registry.setdefault(dept.upper(), []).append(worker_id)

    @classmethod
    def find_available(cls, dept):
        return cls._registry.get(dept.upper(), [None])[0]

class CapabilityDispatcher:
    _lock = threading.Lock()

    @classmethod
    def dispatch(cls, task_id):
        with cls._lock:
            task = WorkflowEngine.get_task(task_id)
            if task.status != "ASSIGN_WORKER": return False
            
            worker = WorkerRegistry.find_available(task.department)
            if worker:
                task.execution_log.append(f"Dispatched to worker: {worker}")
                task.status = "EXECUTE"
                task.checkpoint = "EXECUTE"
                task.update_hash()
                WorkflowEngine._persist(task)
                return True
            return False

import threading
from core.registry import SystemRegistry

class CapabilityHandle:
    def __init__(self, department):
        self._dept = department
    def delegate(self, task):
        # The only way to interact with the department
        return self._dept.execute_task(task)
    def get_status(self):
        return self._dept.kpis

class BaseDepartment:
    def __init__(self, name, chief_worker_name):
        self.name = name
        self.chief_worker = chief_worker_name
        self.kpis = {"budget": 1000, "spent": 0}
        self.lock = threading.Lock()
        SystemRegistry.register_department(name, self)

    def execute_task(self, task):
        # Centralized execution point
        return f"[{self.name}] Chief {self.chief_worker} processed: {task}"

    def get_handle(self):
        return CapabilityHandle(self)

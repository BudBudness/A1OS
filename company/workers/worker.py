from company.base import BaseAgent

class Worker(BaseAgent):
    def __init__(self, name: str, skill: str):
        super().__init__(name, role=f"{skill} Specialist")
        
    def execute(self, task_payload: dict):
        raise NotImplementedError("Implementation required")


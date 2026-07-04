from company.base import BaseAgent

class Manager(BaseAgent):
    def __init__(self, name: str, department: str):
        super().__init__(name, role=f"{department} Manager")
        
    def decompose_task(self, directive: str):
        pass


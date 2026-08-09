from company.base import BaseAgent

class Executive(BaseAgent):
    def __init__(self, name: str, domain: str):
        super().__init__(name, role=f"Chief {domain} Officer")
        self.domain = domain
        
    def formulate_directive(self, objective: str):
        raise NotImplementedError("Implementation required")


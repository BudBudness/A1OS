from company.registry import AgentRegistry

class Orchestrator:
    def __init__(self):
        self.registry = AgentRegistry()

    def get_workers(self):
        return self.registry.get_workers()

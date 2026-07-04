
from company.ceo.agent import CEO
from company.registry import AgentRegistry
from typing import List

class HierarchyEngine:
    def __init__(self, ceo: CEO, registry: AgentRegistry):
        self.ceo = ceo
        self.registry = registry
        self.subordinates: dict = {}

    def assign_report(self, manager_name: str, worker_name: str):
        if manager_name not in self.subordinates:
            self.subordinates[manager_name] = []
        self.subordinates[manager_name].append(worker_name)


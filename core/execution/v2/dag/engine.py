
from typing import List, Dict, Set

class DAG:
    def __init__(self):
        self.graph: Dict[str, Set[str]] = {}
        
    def add_dependency(self, task_id: str, depends_on: str):
        if task_id not in self.graph:
            self.graph[task_id] = set()
        self.graph[task_id].add(depends_on)
        
    def get_execution_order(self) -> List[str]:
        # Implementation for topological sort to follow
        return list(self.graph.keys())


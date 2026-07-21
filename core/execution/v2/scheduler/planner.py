
from typing import List, Dict
from core.execution.v2.scheduler.priority import TaskPriority
from core.execution.v2.dag.engine import DAG

class TaskPlanner:
    def __init__(self, dag: DAG):
        self.dag = dag
        self.schedule: List[str] = []
        
    def plan(self, tasks: Dict[str, TaskPriority]):
        # Topological sort and scheduling logic
        self.schedule = list(tasks.keys())
        return self.schedule



class DAG:
    def __init__(self):
        self.nodes = {}
        
    def add_task(self, task_id: str, dependencies: list):
        self.nodes[task_id] = dependencies


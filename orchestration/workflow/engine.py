from core.execution.v2.dispatcher.engine import DistributedDispatcher

class WorkflowEngine:
    def __init__(self):
        self.dispatcher = DistributedDispatcher()
        self.dispatcher.register("process_data", lambda data: data)
        self.tasks = []

    def _process_data(self, data):
        return data

        self.dispatcher.register("process_data", self._process_data)

    def add_step(self, task_id, action, data):
        self.tasks.append({"task_id": task_id, "action": action, "data": data})

    def run_dag(self):
        results = []
        for task in self.tasks:
            result = self.dispatcher.dispatch(task)
            results.append(result)
        return results

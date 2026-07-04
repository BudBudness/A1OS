class OpsWorker:
    def execute(self, task):
        print(f"OPS: Executing {task['task_type']}")
        return True

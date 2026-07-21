class DevWorker:
    def execute(self, task):
        print(f"DEV: Executing {task['task_type']}")
        return True

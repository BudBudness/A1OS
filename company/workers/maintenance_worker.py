class MaintenanceWorker:
    def execute(self, task):
        print(f"MAINTENANCE: Executing {task['task_type']}")
        return True

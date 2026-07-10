class Scheduler:
    def __init__(self):
        self.queue = []
    
    def add_task(self, task):
        self.queue.append(task)
        return {"task_id": "task_123", "position": len(self.queue)}

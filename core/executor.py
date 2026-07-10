class Executor:
    def __init__(self):
        self.tasks = {}
    
    async def execute(self, task_id, payload):
        self.tasks[task_id] = payload
        return {"task_id": task_id, "status": "executed"}

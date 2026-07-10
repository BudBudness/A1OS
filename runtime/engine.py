class RuntimeEngine:
    def __init__(self):
        self.running = False
        self.tasks = {}
    
    async def start(self):
        self.running = True
        return {"status": "started"}
    
    async def execute(self, task_id: str, payload: dict):
        self.tasks[task_id] = payload
        return {"task_id": task_id, "status": "executed"}
    
    def get_status(self):
        return {"running": self.running, "tasks": len(self.tasks)}

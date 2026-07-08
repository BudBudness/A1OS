class Worker:
    name="security"
    async def execute(self,event):
        return {"worker":"security","status":"ok","event":event}

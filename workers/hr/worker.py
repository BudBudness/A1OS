class Worker:
    name="hr"
    async def execute(self,event):
        return {"worker":"hr","status":"ok","event":event}

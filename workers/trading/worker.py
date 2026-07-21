class Worker:
    name="trading"
    async def execute(self,event):
        return {"worker":"trading","status":"ok","event":event}

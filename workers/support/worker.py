class Worker:
    name="support"
    async def execute(self,event):
        return {"worker":"support","status":"ok","event":event}

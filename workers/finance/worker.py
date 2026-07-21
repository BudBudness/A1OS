class Worker:
    name="finance"
    async def execute(self,event):
        return {"worker":"finance","status":"ok","event":event}

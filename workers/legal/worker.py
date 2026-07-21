class Worker:
    name="legal"
    async def execute(self,event):
        return {"worker":"legal","status":"ok","event":event}

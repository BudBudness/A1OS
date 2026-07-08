class Worker:
    name="research"
    async def execute(self,event):
        return {"worker":"research","status":"ok","event":event}

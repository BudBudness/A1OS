class Worker:
    name="marketing"
    async def execute(self,event):
        return {"worker":"marketing","status":"ok","event":event}

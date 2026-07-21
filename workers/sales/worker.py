class Worker:
    name="sales"
    async def execute(self,event):
        return {"worker":"sales","status":"ok","event":event}

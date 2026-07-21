class Worker:
    name="analytics"
    async def execute(self,event):
        return {"worker":"analytics","status":"ok","event":event}

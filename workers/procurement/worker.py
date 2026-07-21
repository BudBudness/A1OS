class Worker:
    name="procurement"
    async def execute(self,event):
        return {"worker":"procurement","status":"ok","event":event}

class Worker:
    name="devops"
    async def execute(self,event):
        return {"worker":"devops","status":"ok","event":event}

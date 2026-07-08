class Worker:
    name="crm"
    async def execute(self,event):
        return {"worker":"crm","status":"ok","event":event}

class BaseWorker:
    name="base"
    async def execute(self,event):
        raise NotImplementedError

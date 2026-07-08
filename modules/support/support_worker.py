from workers.base_worker import BaseWorker

class SupportWorker(BaseWorker):
    name="support"

    async def execute(self,event):
        return {
            "worker":"support",
            "status":"success",
            "event":event
        }

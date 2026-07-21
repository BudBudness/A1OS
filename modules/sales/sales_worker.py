from workers.base_worker import BaseWorker

class SalesWorker(BaseWorker):
    name="sales"

    async def execute(self,event):
        return {
            "worker":"sales",
            "status":"success",
            "event":event
        }

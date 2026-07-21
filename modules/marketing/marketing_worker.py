from workers.base_worker import BaseWorker

class MarketingWorker(BaseWorker):
    name="marketing"

    async def execute(self,event):
        return {
            "worker":"marketing",
            "status":"success",
            "event":event
        }

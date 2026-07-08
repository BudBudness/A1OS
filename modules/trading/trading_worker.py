from workers.base_worker import BaseWorker

class TradingWorker(BaseWorker):
    name="trading"

    async def execute(self,event):
        return {
            "worker":"trading",
            "status":"success",
            "event":event
        }

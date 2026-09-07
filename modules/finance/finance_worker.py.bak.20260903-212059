from workers.base_worker import BaseWorker

class FinanceWorker(BaseWorker):
    name="finance"

    async def execute(self,event):
        return {
            "worker":"finance",
            "status":"success",
            "event":event
        }

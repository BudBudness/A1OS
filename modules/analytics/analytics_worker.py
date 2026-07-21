from workers.base_worker import BaseWorker

class AnalyticsWorker(BaseWorker):
    name="analytics"

    async def execute(self,event):
        return {
            "worker":"analytics",
            "status":"success",
            "event":event
        }

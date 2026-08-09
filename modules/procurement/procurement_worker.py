from workers.base_worker import BaseWorker

class ProcurementWorker(BaseWorker):
    name="procurement"

    async def execute(self,event):
        return {
            "worker":"procurement",
            "status":"success",
            "event":event
        }

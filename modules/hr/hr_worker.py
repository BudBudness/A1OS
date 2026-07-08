from workers.base_worker import BaseWorker

class HrWorker(BaseWorker):
    name="hr"

    async def execute(self,event):
        return {
            "worker":"hr",
            "status":"success",
            "event":event
        }

from workers.base_worker import BaseWorker

class CrmWorker(BaseWorker):
    name="crm"

    async def execute(self,event):
        return {
            "worker":"crm",
            "status":"success",
            "event":event
        }

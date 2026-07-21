from workers.base_worker import BaseWorker

class ResearchWorker(BaseWorker):
    name="research"

    async def execute(self,event):
        return {
            "worker":"research",
            "status":"success",
            "event":event
        }

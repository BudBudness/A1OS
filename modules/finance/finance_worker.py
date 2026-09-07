from workers.base_worker import BaseWorker
from .engine import FinanceEngine


class FinanceWorker(BaseWorker):
    name = "finance"

    def __init__(self, db="data/a1os.db"):
        self.engine = FinanceEngine(db=db)

    async def execute(self, event):
        if not isinstance(event, dict):
            raise TypeError("Finance worker event must be a dictionary")

        action = event.get("action", "refresh_metrics")
        data = event.get("data", {})
        task_id = event.get("task_id")

        if data is None:
            data = {}

        if not isinstance(data, dict):
            raise TypeError("Finance worker event data must be a dictionary")

        if action == "allocate_funds":
            return await self.engine.process_allocation(data, task_id)

        if action == "process_allocation":
            return await self.engine.process_allocation(data, task_id)

        if action == "refresh_metrics":
            return await self.engine.refresh_metrics()

        return await self.engine.execute(
            action,
            data=data,
            tid=task_id,
        )

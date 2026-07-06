from core.worker import BaseWorker
from typing import Any, Dict

class FinanceWorker(BaseWorker):
    async def execute(self, event: Dict[str, Any]) -> Any:
        return {"status": "finance_processed"}

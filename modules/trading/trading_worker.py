from core.worker import BaseWorker
from typing import Any, Dict

class TradingWorker(BaseWorker):
    async def execute(self, event: Dict[str, Any]) -> Any:
        return {"status": "trading_processed"}

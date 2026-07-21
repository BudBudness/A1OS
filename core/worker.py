from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseWorker(ABC):
    @abstractmethod
    async def execute(self, event: Dict[str, Any]) -> Any:
        pass

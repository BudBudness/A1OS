from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseWorker(ABC):
    @abstractmethod
    @abstractmethod
    async def execute(self, event: Dict[str, Any]) -> Any:
        raise NotImplementedError

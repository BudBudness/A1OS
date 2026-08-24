from abc import ABC, abstractmethod


class ProviderAdapter(ABC):
    name = "unknown"

    @abstractmethod
    async def execute(self, operation, context=None):
        raise NotImplementedError

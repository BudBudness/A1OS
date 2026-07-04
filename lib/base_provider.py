from abc import ABC, abstractmethod

class BaseProvider(ABC):
    @abstractmethod
    def execute(self, action, payload):
        raise NotImplementedError("Implementation required")

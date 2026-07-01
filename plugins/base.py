from abc import ABC, abstractmethod
class A1OSPlugin(ABC):
    @abstractmethod
    def process_event(self, event_type: str, data: dict):
        pass

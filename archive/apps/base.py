
from abc import ABC, abstractmethod

class BaseApp(ABC):
    @abstractmethod
    def run(self, *args, **kwargs):
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass


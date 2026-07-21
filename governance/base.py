
from abc import ABC, abstractmethod
from typing import Any, Dict

class GovernanceController(ABC):
    @abstractmethod
    def validate_policy(self, action: str, context: Dict[str, Any]) -> bool:
        raise NotImplementedError("Implementation required")

    @abstractmethod
    def log_audit_trail(self, event_type: str, details: Dict[str, Any]):
        raise NotImplementedError("Implementation required")


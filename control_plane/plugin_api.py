from abc import ABC, abstractmethod
from typing import Dict, Any

class BasePluginAPI(ABC):
    def __init__(self, name: str, kernel_ref):
        self.name = name
        self.kernel = kernel_ref

    @abstractmethod
    def on_init(self):
        pass

    def request_secret(self, key: str):
        # Enforce CapabilityContract check before vault access
        if self.kernel.contracts.has_access(self.name, "VAULT_READ"):
            return self.kernel.vault.verify(key, "dummy_secret")
        else:
            self.kernel.logger.warning(f"ACCESS DENIED: {self.name} attempted VAULT_READ")
            return None

    def publish_event(self, topic: str, data: Dict[str, Any]):
        # Enforce CapabilityContract check before publishing
        if self.kernel.contracts.has_access(self.name, "EVENT_PUBLISH"):
            self.kernel.bus.publish(topic, data)
        else:
            self.kernel.logger.warning(f"ACCESS DENIED: {self.name} attempted EVENT_PUBLISH")

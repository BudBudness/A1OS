
from typing import Any, Dict
from dataclasses import dataclass

@dataclass
class Message:
    sender: str
    receiver: str
    action: str
    payload: Dict[str, Any]

class AgentProtocol:
    @staticmethod
    def send(message: Message):
        # Implementation for inter-agent messaging
        pass


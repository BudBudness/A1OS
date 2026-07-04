from typing import Any, Dict
from company.protocols.messaging import Message, AgentProtocol

class BaseAgent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def send(self, receiver: str, action: str, payload: Dict[str, Any]):
        AgentProtocol.send(Message(self.name, receiver, action, payload))

    def receive(self, message: Message):
        pass


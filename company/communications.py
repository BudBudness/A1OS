
from company.protocols.messaging import Message
from company.protocols.bus import AgentEventBus

class CommunicationEngine:
    def __init__(self, bus: AgentEventBus):
        self.bus = bus
        
    def broadcast(self, sender: str, action: str, payload: dict):
        self.bus.publish(Message(sender, "ALL", action, payload))


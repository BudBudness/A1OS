
from core.execution.v2.dispatcher.engine import DistributedDispatcher
from company.protocols.messaging import Message

class AgentEventBus(DistributedDispatcher):
    def publish(self, message: Message):
        self.dispatch_task(message.receiver, message.payload)


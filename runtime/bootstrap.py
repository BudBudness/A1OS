from runtime.scheduler.engine import Scheduler
from runtime.bus.event_bus import EventBus
from ai.gateway.engine import AIEngine

class Runtime:
    def __init__(self):
        self.scheduler=Scheduler()
        self.bus=EventBus()
        self.ai=AIEngine()

    async def start(self):
        print("A1OS Runtime Started")

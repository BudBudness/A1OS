from typing import Dict, List, Callable, Any
import asyncio

class EventRouter:
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}
        self.event_queue = asyncio.Queue()
    
    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    async def emit(self, event_type: str, data: Any):
        await self.event_queue.put({"type": event_type, "data": data})
    
    async def process_events(self):
        while True:
            event = await self.event_queue.get()
            if event["type"] in self.handlers:
                for handler in self.handlers[event["type"]]:
                    await handler(event["data"])

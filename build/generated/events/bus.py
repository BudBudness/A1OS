import asyncio

class DecoupledEventBus:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type, callback):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        print(f"[EVENT-BUS] Registered subscriber for topic: {event_type}")

    async def publish(self, event_type, payload):
        if event_type not in self._subscribers:
            return
        for callback in self._subscribers[event_type]:
            if asyncio.iscoroutinefunction(callback):
                await callback(payload)
            else:
                callback(payload)
        print(f"[EVENT-BUS] Dispatched message payload to topic: {event_type}")
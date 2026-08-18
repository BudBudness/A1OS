import asyncio
from typing import Dict, List, Callable, Any, Awaitable

EventHandler = Callable[[Dict[str, Any]], Awaitable[None]]

class MessageBus:
    def __init__(self):
        self.subscribers = {}

    def __init__(self):
        self._subscribers: Dict[str, List[EventHandler]] = {}

    def subscribe(self, topic: str, handler: EventHandler):
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)

    async def publish(self, event, data, priority="normal"):
        import inspect

        callbacks = list(self._subscribers.get(event, []))

        for callback in callbacks:
            result = callback(data)
            if inspect.isawaitable(result):
                await result

        return data

    async def _safely_execute(self, handler: EventHandler, topic: str, payload: Dict[str, Any]):
        try:
            await handler(payload)
        except Exception as e:
            print(f"[MessageBus Exception] Error in topic handler '{topic}': {e}")

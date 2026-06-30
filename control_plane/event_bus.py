import logging
from typing import Dict, List, Callable

logger = logging.getLogger("A1OS-EventBus")

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, data: Dict):
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(data)
        logger.info(f"[EVENTBUS] Published: {event_type}")

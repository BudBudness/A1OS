import threading

class EventBus:
    _subscribers = {}
    _lock = threading.Lock()

    @classmethod
    def subscribe(cls, event_type, callback):
        with cls._lock:
            cls._subscribers.setdefault(event_type, []).append(callback)

    @classmethod
    def publish(cls, event_type, data):
        for callback in cls._subscribers.get(event_type, []):
            callback(data)

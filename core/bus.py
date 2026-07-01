class EventBus:
    subscribers = {}
    @classmethod
    def subscribe(cls, event_type, callback):
        if event_type not in cls.subscribers: cls.subscribers[event_type] = []
        cls.subscribers[event_type].append(callback)
    @classmethod
    def emit(cls, event_type, data):
        for callback in cls.subscribers.get(event_type, []):
            callback(data)

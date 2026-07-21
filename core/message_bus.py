class MessageBus:
    def __init__(self): 
        self.subscribers = {"high": {}, "normal": {}}

    def subscribe(self, event, callback, priority="normal"):
        self.subscribers[priority].setdefault(event, []).append(callback)

    def publish(self, event, data, priority="normal"):
        # Execute high priority first
        for callback in self.subscribers["high"].get(event, []):
            callback(data)
        # Then normal priority
        for callback in self.subscribers[priority].get(event, []):
            callback(data)

class MessageBus:
    def __init__(self): 
        self.subscribers = {"high": {}, "normal": {}}

    def subscribe(self, event, callback, priority="normal"):
        self.subscribers[priority].setdefault(event, []).append(callback)

    async def publish(self, event, data, priority="normal"):
        import inspect

        for callback in self.subscribers["high"].get(event, []):
            result = callback(data)
            if inspect.isawaitable(result):
                await result

        for callback in self.subscribers[priority].get(event, []):
            result = callback(data)
            if inspect.isawaitable(result):
                await result

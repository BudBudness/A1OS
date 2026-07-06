class MessageBus:
    def __init__(self):
        self.backend = "redis"  # swap: redis | nats | kafka

    async def publish(self, topic, message):
        # production hook for distributed queue
        pass

    async def subscribe(self, topic, handler):
        pass

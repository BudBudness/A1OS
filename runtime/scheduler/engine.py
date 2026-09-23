class Scheduler:
    async def schedule(self, event):
        if not isinstance(event, dict):
            raise TypeError("scheduled event must be a mapping")
        return event

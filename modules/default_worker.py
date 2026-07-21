class DefaultWorker:
    async def execute(self, event):
        return {"status": "processed", "event": event}
def register(runtime):
    runtime.workers["default"] = DefaultWorker()

class FinanceWorker:
    def __init__(self):
        self.name = "finance"
        self.status = "active"
    
    async def process(self, payload: dict) -> dict:
        action = payload.get('action', 'default')
        return {
            "status": "success",
            "data": payload,
            "worker": self.name,
            "action": action,
            "processed": True
        }

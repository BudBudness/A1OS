class SalesWorker:
    def __init__(self):
        self.name = "sales"
        self.status = "active"
    
    async def process(self, payload: dict) -> dict:
        return {
            "status": "success",
            "data": payload,
            "worker": self.name,
            "processed": True
        }

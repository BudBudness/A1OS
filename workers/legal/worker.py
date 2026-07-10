class LegalWorker:
    def __init__(self):
        self.name = "legal"
        self.status = "active"
    
    async def process(self, payload: dict) -> dict:
        return {
            "status": "success",
            "data": payload,
            "worker": self.name,
            "processed": True
        }

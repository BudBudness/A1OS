class SalesEngine:
    async def execute(self, action, **kwargs):
        data = kwargs.get("data", {})
        task_id = kwargs.get("task_id")
        return await self.process_order(data, task_id)

    async def process_order(self, d: dict, tid: str) -> dict:
        print(f"   ⚙️ [SalesEngine Pipeline Intercept] Order validated for tracking ID: {tid}")
        return {"status": "order_validated", "item": d.get("item"), "value": d.get("value")}

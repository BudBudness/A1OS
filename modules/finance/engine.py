import sqlite3
class FinanceEngine:
    async def execute(self, action, **kwargs):
        method = getattr(self, action, None)

        if method is None or not callable(method):
            raise RuntimeError(
                f"Finance engine has no compatible action: {action}"
            )

        data = kwargs.pop("data", {})
        if data is None:
            data = {}
        if not isinstance(data, dict):
            raise TypeError("Finance execution data must be a dictionary")

        arguments = {
            key: value
            for key, value in kwargs.items()
            if key not in {"target", "action", "role"}
        }
        arguments.update(data)

        result = method(**arguments)
        if hasattr(result, "__await__"):
            return await result
        return result


    def __init__(self, db="a1os_state.db"): self.db = db
    async def process_allocation(self, d: dict, tid: str = None) -> dict:
        asset = d.get("item", "unallocated_reserve")
        amount = max(0.0, float(d.get("value", 0)))
        with sqlite3.connect(self.db, timeout=10.0) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO finance_ledger (asset_name, allocation_type, amount, reference_task_id) VALUES (?,?,?,?)", (asset, "WORKFLOW_ALLOCATION", amount, tid))
            c.execute("SELECT SUM(amount) FROM finance_ledger WHERE asset_name = ?", (asset,))
            tot = c.fetchone()[0] or 0.0
            conn.commit()
        print(f"      [FinanceEngine] Ledger pools synchronized. Asset: '{asset}' | Total: {tot} UGX")
        return {"asset": asset, "current_balance": tot}

import sqlite3
class BillingEngine:
    async def execute(self, action, **kwargs):
        method = getattr(self, action, None)

        if method is None or not callable(method):
            raise RuntimeError(
                f"Billing engine has no compatible action: {action}"
            )

        data = kwargs.pop("data", {})
        if data is None:
            data = {}
        if not isinstance(data, dict):
            raise TypeError("Billing execution data must be a dictionary")

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
    async def generate_invoice(self, d: dict) -> dict:
        inv = d.get("invoice_id", "INV-GENERIC")
        cid = d.get("customer_id", "CUST-GENERIC")
        amt = float(d.get("amount", 0.0))
        with sqlite3.connect(self.db, timeout=10.0) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO billing_invoices (invoice_id, customer_id, amount, status) VALUES (?,?,?,?) ON CONFLICT(invoice_id) DO UPDATE SET status=excluded.status", (inv, cid, amt, d.get("status", "UNPAID")))
            conn.commit()
        print(f"      [BillingEngine] Relational invoice ledger entry generated. Reference ID: {inv} | Amt: {amt} UGX")
        return {"invoice_id": inv, "status": d.get("status", "UNPAID")}

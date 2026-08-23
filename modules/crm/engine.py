import sqlite3
class CRMEngine:
    async def execute(self, action, **kwargs):
        method = getattr(self, action, None)

        if method is None or not callable(method):
            raise RuntimeError(
                f"CRM engine has no compatible action: {action}"
            )

        data = kwargs.pop("data", {})
        if data is None:
            data = {}
        if not isinstance(data, dict):
            raise TypeError("CRM execution data must be a dictionary")

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
    async def update_profile(self, d: dict) -> dict:
        cid = d.get("customer_id", "CUST-UNKNOWN")
        name = d.get("name", "Standard Client Profile")
        val = float(d.get("value", 0.0))
        with sqlite3.connect(self.db, timeout=10.0) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO crm_profiles (customer_id, name, lifetime_value) VALUES (?,?,?) ON CONFLICT(customer_id) DO UPDATE SET lifetime_value=lifetime_value+excluded.lifetime_value, updated_at=CURRENT_TIMESTAMP", (cid, name, val))
            c.execute("SELECT lifetime_value FROM crm_profiles WHERE customer_id=?", (cid,))
            ltv = c.fetchone()[0]
            tier = "GOLD" if ltv >= 1000000 else "SILVER" if ltv >= 500000 else "BRONZE"
            c.execute("UPDATE crm_profiles SET tier=? WHERE customer_id=?", (tier, cid))
            conn.commit()
        print(f"      [CRMEngine] Profile tracking sync complete. Customer: {cid} | Segment Tier: {tier} | LTV: {ltv} UGX")
        return {"customer_id": cid, "tier": tier, "lifetime_value": ltv}

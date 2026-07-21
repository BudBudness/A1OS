import sqlite3
class InventoryEngine:
    def __init__(self, db="a1os_state.db"): self.db = db
    async def adjust_stock(self, d: dict) -> dict:
        sku = d.get("sku", "SKU-GENERIC")
        qty = int(d.get("qty", 0))
        loc = d.get("location", "Mbarara_Central")
        with sqlite3.connect(self.db, timeout=10.0) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO inventory_registry (sku, name, quantity, location) VALUES (?,?,?,?) ON CONFLICT(sku) DO UPDATE SET quantity=quantity+excluded.quantity, updated_at=CURRENT_TIMESTAMP", (sku, d.get("name", "Asset Component"), qty, loc))
            c.execute("SELECT quantity FROM inventory_registry WHERE sku=?", (sku,))
            cur = c.fetchone()[0]
            conn.commit()
        print(f"      [InventoryEngine] Physical stock structural update. SKU: {sku} | New Bal: {cur} units.")
        return {"sku": sku, "current_stock": cur}

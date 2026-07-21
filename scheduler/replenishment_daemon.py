import sqlite3

def run_replenishment():
    with sqlite3.connect("a1os_state.db") as conn:
        c = conn.cursor()
        c.execute("SELECT sku, name FROM inventory_registry WHERE quantity <= 5")
        items = c.fetchall()
        for sku, name in items:
            print(f"📦 [AUTO-PROCUREMENT] Triggered order for: {name} ({sku})")
            try:
                c.execute("INSERT INTO finance_ledger (id, asset_name, amount) VALUES (?, ?, ?)", 
                          (f"PO-{sku}", f"Restock Order: {name}", -150000.00))
            except sqlite3.IntegrityError:
                pass
        conn.commit()

if __name__ == "__main__":
    run_replenishment()

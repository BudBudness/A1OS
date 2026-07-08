import sqlite3

def calculate_demand_forecast(sku, product_name):
    with sqlite3.connect("a1os_state.db") as conn:
        c = conn.cursor()
        # Look for the product name in the ledger regardless of the transaction prefix
        c.execute("SELECT amount FROM finance_ledger WHERE asset_name LIKE ?", (f"%{product_name}%",))
        sales_history = [row[0] for row in c.fetchall() if row[0] > 0]
        
        c.execute("SELECT COUNT(*) FROM crm_profiles WHERE tier = 'GOLD'")
        gold_count = c.fetchone()[0]
        
        # Calculate mean velocity
        avg_velocity = (sum(sales_history) / len(sales_history)) if sales_history else 0
        buffer = 1.5 if gold_count > 1 else 1.0
        
        return avg_velocity * buffer

def run_prediction_matrix():
    print("🧠 [AI REASONER] Mapping Inventory-to-Ledger Velocity...")
    with sqlite3.connect("a1os_state.db") as conn:
        c = conn.cursor()
        c.execute("SELECT sku, name FROM inventory_registry")
        for sku, name in c.fetchall():
            forecast = calculate_demand_forecast(sku, name)
            print(f"   ▪️ {sku:<15} | Predicted Demand: {forecast:,.2f} UGX")
            if forecast > 500000:
                print(f"   💡 [PROACTIVE] AI suggests pre-emptive stock increase for {name}")

if __name__ == "__main__":
    run_prediction_matrix()

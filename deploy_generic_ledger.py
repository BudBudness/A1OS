import sqlite3

DB_PATH = "a1os_state.db"

# 1. Inject diversified revenue streams to test the generic ledger processing
with sqlite3.connect(DB_PATH) as conn:
    c = conn.cursor()
    
    # Ensure finance table exists
    c.execute("""
        CREATE TABLE IF NOT EXISTS finance_ledger (
            id TEXT PRIMARY KEY,
            asset_name TEXT,
            amount REAL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Clean old static data and seed dynamic retail revenue lines
    c.execute("DELETE FROM finance_ledger;")
    revenue_payloads = [
        ("REV-001", "Premium Tier License", 1800000.00),
        ("REV-002", "Hardware Sales (Kampala)", 2450000.00),
        ("REV-003", "Studio Bookings (Mbarara)", 620000.00)
    ]
    c.executemany("""
        INSERT INTO finance_ledger (id, asset_name, amount)
        VALUES (?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET amount = EXCLUDED.amount
    """, revenue_payloads)
    conn.commit()

# 2. Overwrite dashboard_ui.py with the dynamic loop architecture
dashboard_code = """import sqlite3
import os

DB_PATH = "a1os_state.db"

def format_currency(val):
    return f"{val:,.2f} UGX"

def run_dashboard():
    os.system("clear")
    print("=================================================================")
    print("🛡️                 A1OS MULTI-MATRIX SYSTEM CORE                 🛡️")
    print("=================================================================")
    
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        # 1. COMPLETELY GENERIC FINANCIAL LEDGER LOOP
        print("\\n💸 [DYNAMIC FINANCIAL BALANCE SHEET]")
        c.execute("SELECT asset_name, SUM(amount) FROM finance_ledger GROUP BY asset_name ORDER BY SUM(amount) DESC")
        rows = c.fetchall()
        if not rows:
            print("   No active asset ledger pools initialized.")
        for row in rows:
            clean_asset = row[0].replace("_", " ").title()
            gross = row[1]
            vat = gross * 0.18
            net_revenue = gross - vat
            print(f"   ▪️ {clean_asset:<25} | Gross: {format_currency(gross)}")
            print(f"                             | VAT (18%): {format_currency(vat)}")
            print(f"                             | Net Profit: {format_currency(net_revenue)}")
            print(f"                             -----------------------------------")
        
        # 2. Dynamic Inventory Control Matrix
        print("\\n📦 [MULTI-WAREHOUSE INVENTORY & LOGISTICS CONTROL]")
        c.execute("SELECT sku, name, quantity, location FROM inventory_registry")
        rows = c.fetchall()
        for row in rows:
            clean_loc = row[3].replace("_", " ").title()
            alert_status = " ⚠️ [LOW STOCK CRITICAL ALERT]" if row[2] <= 5 else ""
            print(f"   ▪️ [{row[0]}] {row[1]:<26} | Qty: {row[2]:<3} | Loc: {clean_loc}{alert_status}")
            
        # 3. Dynamic CRM Client Status Mapping
        print("\\n👥 [LOYALTY MEMBER TARGET PROFILES]")
        c.execute("SELECT customer_id, name, tier, lifetime_value FROM crm_profiles ORDER BY lifetime_value DESC")
        rows = c.fetchall()
        for row in rows:
            tier_badge = f"🥇 {row[2]}" if row[2] == "GOLD" else f"🥈 {row[2]}" if row[2] == "SILVER" else f"🥉 {row[2]}"
            print(f"   ▪️ Handle: {row[0]:<15} | Name: {row[1]:<20} | Rank: {tier_badge:<8} | Total LTV: {format_currency(row[3])}")
            
        # 4. Outbound Telemetry Network Matrix
        print("\\n📡 [EDGE INSTANCE CONNECTIVITY & METRICS]")
        c.execute("SELECT status, COUNT(*) FROM notification_history GROUP BY status")
        rows = c.fetchall()
        sent_count = sum(r[1] for r in rows if "SENT" in r[0] or "FLUSHED" in r[0])
        fail_count = sum(r[1] for r in rows if "FAILED" in r[0])
        total_sync = sent_count + fail_count
        
        sync_rate = (sent_count / total_sync * 100) if total_sync > 0 else 0.0
        print(f"   ▪️ Interface Network Status: ONLINE (Dynamic Asset Sync)")
        print(f"   ▪️ Edge Delivery Success   : {sync_rate:.1f}% Delivery Rate")
        print(f"   ▪️ Operational Dispatches  : {sent_count:<4} packets pushed upstream.")
        print(f"   ▪️ Locally Cached Backlog  : {fail_count:<4} packets pending network recovery.")
        
    print("\\n=================================================================")

if __name__ == "__main__":
    run_dashboard()
"""

with open("dashboard_ui.py", "w") as f:
    f.write(dashboard_code)

print("⚡ Generic financial schema updates and dynamic UI compiled successfully.")

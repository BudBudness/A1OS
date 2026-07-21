import sqlite3
import os

DB_PATH = "a1os_state.db"

def format_currency(val):
    return f"{val:,.2f} UGX"

def run_dashboard():
    os.system("clear")
    print("=================================================================")
    print("🛡️                 A1OS ENTERPRISE MANAGEMENT SYSTEM             🛡️")
    print("=================================================================")
    
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        # 1. Financial Ledger Mapping with 18% VAT Split
        print("\n💸 [FINANCIAL LEDGER BALANCE SHEET]")
        c.execute("SELECT asset_name, SUM(amount) FROM finance_ledger GROUP BY asset_name")
        rows = c.fetchall()
        if not rows:
            print("   No active asset ledger pools initialized.")
        for row in rows:
            clean_asset = row[0].replace("_", " ").title()
            gross = row[1]
            vat = gross * 0.18
            net_revenue = gross - vat
            print(f"   ▪️ {clean_asset:<22} | Gross: {format_currency(gross)}")
            print(f"                            | 18% UGX VAT: {format_currency(vat)}")
            print(f"                            | Net Profit : {format_currency(net_revenue)}")
        
        # 2. Dynamic Inventory Matrix & Low Stock Alerts
        print("\n📦 [MULTI-WAREHOUSE INVENTORY & LOGISTICS CONTROL]")
        c.execute("SELECT sku, name, quantity, location FROM inventory_registry")
        rows = c.fetchall()
        if not rows:
            print("   Warehouse inventory empty.")
        for row in rows:
            clean_loc = row[3].replace("_", " ").title()
            alert_status = ""
            if row[2] <= 5:
                alert_status = " ⚠️ [LOW STOCK CRITICAL ALERT]"
            print(f"   ▪️ [{row[0]}] {row[1]:<26} | Qty: {row[2]:<3} | Loc: {clean_loc}{alert_status}")
            
        # 3. Dynamic CRM Client Status Mapping
        print("\n👥 [LOYALTY MEMBER TARGET PROFILES]")
        c.execute("SELECT customer_id, name, tier, lifetime_value FROM crm_profiles ORDER BY lifetime_value DESC")
        rows = c.fetchall()
        if not rows:
            print("   CRM profile records uninitialized.")
        for row in rows:
            tier_badge = f"🥇 {row[2]}" if row[2] == "GOLD" else f"🥈 {row[2]}" if row[2] == "SILVER" else f"🥉 {row[2]}"
            print(f"   ▪️ Handle: {row[0]:<15} | Name: {row[1]:<20} | Rank: {tier_badge:<8} | Total LTV: {format_currency(row[3])}")
            
        # 4. Outbound Telemetry Network SLA Matrix
        print("\n📡 [EDGE INSTANCE CONNECTIVITY & METRICS]")
        c.execute("SELECT status, COUNT(*) FROM notification_history GROUP BY status")
        rows = c.fetchall()
        sent_count = sum(r[1] for r in rows if "SENT" in r[0] or "FLUSHED" in r[0])
        fail_count = sum(r[1] for r in rows if "FAILED" in r[0])
        total_sync = sent_count + fail_count
        
        sync_rate = (sent_count / total_sync * 100) if total_sync > 0 else 0.0
        print(f"   ▪️ Interface Network Status: ONLINE (Simulated Tracking)")
        print(f"   ▪️ Edge Delivery Success   : {sync_rate:.1f}% Delivery Rate")
        print(f"   ▪️ Operational Dispatches  : {sent_count:<4} packets pushed upstream.")
        print(f"   ▪️ Locally Cached Backlog  : {fail_count:<4} packets pending network recovery.")
        
    print("\n=================================================================")

if __name__ == "__main__":
    run_dashboard()

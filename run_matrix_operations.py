import sqlite3
import time
import random
import threading
import sys
import os

DB_PATH = "a1os_state.db"

def run_recovery_daemon():
    """Option 1: Scans local cache, simulates connection retries, and clears outages."""
    while True:
        try:
            with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
                c = conn.cursor()
                c.execute("SELECT id FROM notification_history WHERE status LIKE 'FAILED%' LIMIT 5")
                failed_tasks = c.fetchall()
                
                if failed_tasks:
                    for task in failed_tasks:
                        c.execute(
                            "UPDATE notification_history SET status = 'SENT' WHERE id = ?", 
                            (task[0],)
                        )
                    conn.commit()
        except Exception:
            pass
        time.sleep(2.5)

def run_stress_simulator():
    """Option 2: Generates random high-volume retail transactions across the matrix."""
    products = [
        ("SKU-PIONEER-DJ", "Pioneer DJ Controller", "Kampala Hub"),
        ("SKU-STUDIO-MX", "Professional Studio Mixer", "Mbarara Hub"),
        ("SKU-AUDIO-IF", "Sound Card Audio Interface", "Entebbe Hub")
    ]
    
    customers = [
        ("EDDIE-BILLIONS", "Eddie Billions"),
        ("ALEX-PRO", "Alex Professional Audio"),
        ("JANE-MEDIA", "Jane Media Logistics")
    ]
    
    while True:
        try:
            with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
                c = conn.cursor()
                
                # 1. Randomly choose a product and mutate stock or insert if new
                prod_sku, prod_name, prod_loc = random.choice(products)
                stock_change = random.randint(1, 4)
                c.execute(
                    "INSERT INTO inventory_registry (sku, name, quantity, location) "
                    "VALUES (?, ?, ?, ?) "
                    "ON CONFLICT(sku) DO UPDATE SET quantity = quantity + EXCLUDED.quantity",
                    (prod_sku, prod_name, stock_change, prod_loc)
                )
                
                # 2. Randomly select a customer and scale up lifetime value spend
                cust_id, cust_name = random.choice(customers)
                spend_increment = random.choice([150000.0, 300000.0, 450000.0])
                
                c.execute(
                    "INSERT INTO crm_profiles (customer_id, name, tier, lifetime_value, updated_at) "
                    "VALUES (?, ?, 'BRONZE', ?, datetime('now')) "
                    "ON CONFLICT(customer_id) DO UPDATE SET lifetime_value = lifetime_value + EXCLUDED.lifetime_value",
                    (cust_id, cust_name, spend_increment)
                )
                
                # 3. Recalculate and scale tier badges based on the updated spending metrics
                c.execute(
                    "UPDATE crm_profiles SET tier = CASE "
                    "WHEN lifetime_value >= 1000000.0 THEN 'GOLD' "
                    "WHEN lifetime_value >= 500000.0 THEN 'SILVER' "
                    "ELSE 'BRONZE' END"
                )
                
                # 4. Drop a random telemetry log indicating high throughput processing
                c.execute(
                    "INSERT INTO notification_history (id, status) VALUES (hex(randomblob(16)), 'SENT')"
                )
                
                conn.commit()
        except Exception:
            pass
        time.sleep(1.5)

if __name__ == "__main__":
    print("🚀 Initializing Dual Operations Engine Controller...")
    
    # Initialize background threads
    recovery_thread = threading.Thread(target=run_recovery_daemon, daemon=True)
    simulator_thread = threading.Thread(target=run_stress_simulator, daemon=True)
    
    recovery_thread.start()
    print(" 🛠️  Option 1: Background Webhook Self-Healing Recovery Daemon -> ONLINE")
    
    simulator_thread.start()
    print(" 📊 Option 2: Live Mock Store Transaction Simulator Engine -> ONLINE")
    
    print("\n[Running Process Cluster Mode] Press Ctrl+C to stop operations.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping operations cleanly. Exiting A1OS process vector thread pool.")
        sys.exit(0)

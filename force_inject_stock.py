import sqlite3

DB_PATH = "a1os_state.db"

with sqlite3.connect(DB_PATH) as conn:
    c = conn.cursor()
    
    # 1. Expand the inventory pool to break out of the single controller lock
    gear_items = [
        ("SKU-STUDIO-MX", "Professional Studio Mixer", 4, "Mbarara Hub"),
        ("SKU-AUDIO-IF", "Sound Card Audio Interface", 3, "Entebbe Hub"),
        ("SKU-MONITOR-X", "Active Studio Monitors", 12, "Kampala Hub")
    ]
    c.executemany("""
        INSERT INTO inventory_registry (sku, name, quantity, location)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(sku) DO UPDATE SET quantity = quantity + EXCLUDED.quantity
    """, gear_items)
    
    # 2. Diversify client database tracking with varied tiers
    fresh_profiles = [
        ("ALEX-PRO", "Alex Professional Audio", "SILVER", 750000.00),
        ("JANE-MEDIA", "Jane Media Logistics", "BRONZE", 320000.00)
    ]
    c.executemany("""
        INSERT INTO crm_profiles (customer_id, name, tier, lifetime_value, updated_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        ON CONFLICT(customer_id) DO UPDATE SET lifetime_value = lifetime_value + EXCLUDED.lifetime_value
    """, fresh_profiles)

    conn.commit()

print("⚡ Core injection complete. Inventory matrix diversified.")

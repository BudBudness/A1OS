from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import sqlite3
import os

app = FastAPI()

DB_PATH = "a1os_state.db"

class MobileRequest(BaseModel):
    action: str  # Supported actions: "place_order"
    payload: Dict[str, Any]

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="A1OS Core Database state file not found.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enables named column lookups
    return conn

@app.get("/mobile/sync")
async def sync_data():
    """Fetches real-time cluster data to synchronize mobile app instances."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            
            # Fetch generic inventory assets
            c.execute("SELECT sku, name, quantity, location FROM inventory_registry")
            inventory = [dict(row) for row in c.fetchall()]
            
            # Fetch dynamic ledger metrics
            c.execute("SELECT asset_name, SUM(amount) as total_gross FROM finance_ledger GROUP BY asset_name")
            finance = []
            for row in c.fetchall():
                gross = row["total_gross"]
                vat = gross * 0.18
                finance.append({
                    "asset_name": row["asset_name"],
                    "gross_ugx": gross,
                    "vat_18_ugx": vat,
                    "net_profit_ugx": gross - vat
                })
                
            return {
                "status": "synchronized",
                "version": "2.0.0",
                "payload": {
                    "inventory": inventory,
                    "financial_summary": finance
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synchronization failure: {str(e)}")

@app.post("/mobile/action")
async def mobile_action(request: MobileRequest):
    """Processes inbound device pipeline transactions with atomic database isolation."""
    if request.action != "place_order":
        raise HTTPException(status_code=400, detail=f"Action type '{request.action}' unsupported by mobile gateway.")
        
    payload = request.payload
    sku = payload.get("sku")
    qty = payload.get("quantity", 1)
    customer_id = payload.get("customer_id")
    unit_price = payload.get("unit_price", 0.0)
    
    if not sku or not customer_id:
        raise HTTPException(status_code=400, detail="Missing structural parameters: 'sku' and 'customer_id' required.")

    total_gross = unit_price * qty

    try:
        with get_db_connection() as conn:
            # Set WAL-compatible isolation timeout to handle high-concurrency environments
            conn.execute("PRAGMA busy_timeout = 5000;")
            c = conn.cursor()
            
            # 1. Verify stock availability
            c.execute("SELECT quantity, name FROM inventory_registry WHERE sku = ?", (sku,))
            item = c.fetchone()
            if not item:
                raise HTTPException(status_code=404, detail=f"Item matching SKU '{sku}' not found in registry.")
                
            current_stock = item["quantity"]
            product_name = item["name"]
            if current_stock < qty:
                raise HTTPException(status_code=400, detail=f"Insufficient inventory stock. Requested: {qty}, Available: {current_stock}")
                
            # 2. Begin Atomic Database Transaction
            c.execute("BEGIN TRANSACTION;")
            
            # 3. Deduct Inventory Stock Level
            c.execute("UPDATE inventory_registry SET quantity = quantity - ? WHERE sku = ?", (qty, sku))
            
            # 4. Inject Dynamic Ledger Revenue Split
            ledger_id = f"REV-MOB-{os.urandom(4).hex().upper()}"
            asset_label = f"Mobile Sales ({product_name})"
            c.execute("""
                INSERT INTO finance_ledger (id, asset_name, amount)
                VALUES (?, ?, ?)
            """, (ledger_id, asset_label, total_gross))
            
            # 5. Mutate CRM Customer Lifetime Value Metrics
            c.execute("""
                INSERT INTO crm_profiles (customer_id, name, tier, lifetime_value)
                VALUES (?, ?, 'BRONZE', ?)
                ON CONFLICT(customer_id) DO UPDATE SET 
                    lifetime_value = lifetime_value + EXCLUDED.lifetime_value,
                    updated_at = CURRENT_TIMESTAMP
            """, (customer_id, customer_id.replace("-", " ").title(), total_gross))
            
            # Recalculate dynamic CRM loyalty status threshold
            c.execute("SELECT lifetime_value FROM crm_profiles WHERE customer_id = ?", (customer_id,))
            updated_ltv = c.fetchone()["lifetime_value"]
            
            new_tier = "BRONZE"
            if updated_ltv >= 1000000.00:
                new_tier = "GOLD"
            elif updated_ltv >= 500000.00:
                new_tier = "SILVER"
                
            c.execute("UPDATE crm_profiles SET tier = ? WHERE customer_id = ?", (new_tier, customer_id))
            
            conn.commit()
            
            return {
                "status": "transaction_processed",
                "action": request.action,
                "summary": {
                    "product": product_name,
                    "quantity_deducted": qty,
                    "gross_revenue_ugx": total_gross,
                    "customer_id": customer_id,
                    "assigned_tier": new_tier
                }
            }
            
    except sqlite3.Error as se:
        raise HTTPException(status_code=500, detail=f"Transactional roll-back triggered: {str(se)}")
    except Exception as e:
        raise e

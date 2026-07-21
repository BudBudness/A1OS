import urllib.request, json
from security.auth.engine import AuthEngine

TARGET_URL = "http://localhost:3001/v1/execute"
auth = AuthEngine()

def fire(target, action, role, data):
    payload = {"target": target, "action": action, "role": role, "data": data}
    sig = auth.generate_signature(payload)
    req = urllib.request.Request(TARGET_URL, data=json.dumps(payload, sort_keys=True).encode("utf-8"), headers={"Content-Type": "application/json", "X-Signature": sig}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200: print(f"🚀 [Gateway Broadcast] Transmitted target load to processing node '{target}'.")
    except Exception as e: print(f"❌ [Gateway Node Error] Matrix reject: {e}")

if __name__ == "__main__":
    print("--- Dispensing Complete 24-Engine Micro-Kernel Simulation Workloads ---")
    # Pipeline 1: Sales Intercept routing to Finance
    fire("sales_module", "create_order", "user", {"item": "premium_tier_license", "value": 450000})
    # Pipeline 2: Stock Allocation adjustments
    fire("inventory_module", "adjust_stock_level", "operator", {"sku": "SKU-PIONEER-DJ", "name": "Pioneer DJ Controller", "qty": 5, "location": "Kampala_Hub"})
    # Pipeline 3: CRM Profile Ledger Segmentation Engine updates
    fire("crm_module", "sync_customer_metrics", "analyst", {"customer_id": "EDDIE-BILLIONS", "name": "Eddie Billions", "value": 650000})
    # Pipeline 4: Commercial Invoicing Generation and processing
    fire("billing_module", "issue_invoice", "billing_service", {"invoice_id": "INV-2026-001", "customer_id": "EDDIE-BILLIONS", "amount": 1350000, "status": "PAID"})

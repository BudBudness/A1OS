from pathlib import Path
import json
from datetime import datetime
import sys

if len(sys.argv) < 2:
    print("Usage: python3 billing_revenue_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "billing_revenue"

layers = [
    "customers",
    "subscriptions",
    "plans",
    "invoices",
    "payments",
    "transactions",
    "reports",
    "analytics",
    "forecasting",
    "audit"
]

for layer in layers:
    (root / layer).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "factory_version": "4.3",
    "status": "billing_revenue_ready",
    "generated": datetime.utcnow().isoformat(),
    "capabilities": [
        "Subscription Management",
        "Invoice Automation",
        "Payment Integration",
        "Revenue Intelligence",
        "Financial Analytics"
    ]
}

(root / "BILLING_REVENUE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Billing Revenue Plane Generated: {product}")

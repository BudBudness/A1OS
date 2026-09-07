import json
import sys
from pathlib import Path
from datetime import datetime, timezone

if len(sys.argv) < 2:
    print("Usage: python3 digital_operations_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "digital_operations"

folders = [
    "operations_center",
    "runbooks",
    "incidents",
    "remediation",
    "changes",
    "maintenance",
    "intelligence",
    "analytics"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "plane": "digital_operations",
    "version": "5.3",
    "generated": datetime.now(timezone.utc).isoformat(),
    "status": "operations_ready",
    "capabilities": [
        "operations_center",
        "runbook_automation",
        "incident_management",
        "automated_remediation",
        "operational_intelligence"
    ]
}

(root / "DIGITAL_OPERATIONS_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Digital Operations Plane Generated: {product}")

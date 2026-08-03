from pathlib import Path
import json
from datetime import datetime
import sys

if len(sys.argv) < 2:
    print("Usage: python3 tenant_control_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "tenant_control"

layers = [
    "tenants",
    "organizations",
    "workspaces",
    "identity",
    "billing",
    "entitlements",
    "governance",
    "analytics"
]

for layer in layers:
    (root / layer).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "factory_version": "4.1",
    "status": "tenant_control_ready",
    "generated": datetime.utcnow().isoformat(),
    "capabilities": layers
}

(root / "TENANT_CONTROL_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Tenant Control Plane Generated: {product}")

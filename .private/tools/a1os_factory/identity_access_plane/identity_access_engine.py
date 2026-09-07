from pathlib import Path
import json
from datetime import datetime
import sys

if len(sys.argv) < 2:
    print("Usage: python3 identity_access_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "identity_access"

layers = [
    "users",
    "roles",
    "permissions",
    "policies",
    "sessions",
    "tokens",
    "service_accounts",
    "audit"
]

for layer in layers:
    (root / layer).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "factory_version": "4.2",
    "status": "identity_access_ready",
    "generated": datetime.utcnow().isoformat(),
    "capabilities": [
        "SSO",
        "RBAC",
        "ABAC",
        "Zero Trust",
        "Identity Governance"
    ]
}

(root / "IDENTITY_ACCESS_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Identity Access Plane Generated: {product}")

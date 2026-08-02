from pathlib import Path
import json
from datetime import datetime
import sys

if len(sys.argv) < 2:
    print("Usage: python3 security_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "security"

layers = {
    "policies": {},
    "rbac": {},
    "compliance": {},
    "audit": {},
    "scanning": {},
    "data_protection": {},
    "monitoring": {}
}

for layer in layers:
    (root / layer).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "factory_version": "3.2",
    "status": "security_ready",
    "generated": datetime.utcnow().isoformat(),
    "security_domains": list(layers.keys())
}

(root / "SECURITY_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Security Plane Generated: {product}")

from pathlib import Path
import json
from datetime import datetime
import sys

if len(sys.argv) < 2:
    print("Usage: python3 marketplace_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "marketplace_ecosystem"

layers = {
    "catalog": {},
    "plugins": {},
    "partners": {},
    "licensing": {},
    "subscriptions": {},
    "tenants": {},
    "analytics": {},
    "intelligence": {}
}

for layer in layers:
    (root / layer).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "factory_version": "4.0",
    "status": "marketplace_ecosystem_ready",
    "generated": datetime.utcnow().isoformat(),
    "components": list(layers.keys())
}

(root / "MARKETPLACE_ECOSYSTEM_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Marketplace Ecosystem Plane Generated: {product}")

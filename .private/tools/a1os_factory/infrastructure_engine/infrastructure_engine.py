from pathlib import Path
import json
from datetime import datetime
import sys

if len(sys.argv) < 2:
    print("Usage: python3 infrastructure_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "infrastructure"

layers = {
    "terraform": {},
    "ansible": {},
    "kubernetes": {},
    "environments": {},
    "secrets": {},
    "validation": {}
}

for layer in layers:
    (root / layer).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "factory_version": "3.1",
    "status": "infrastructure_ready",
    "generated": datetime.utcnow().isoformat(),
    "components": list(layers.keys())
}

(root / "INFRASTRUCTURE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Infrastructure Engine Generated: {product}")

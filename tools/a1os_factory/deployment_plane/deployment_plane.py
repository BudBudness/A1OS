from pathlib import Path
import json
from datetime import datetime

import sys

if len(sys.argv) < 2:
    print("Usage: python3 deployment_plane.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "deployments"

layers = {
    "docker": {},
    "database": {},
    "cicd": {},
    "monitoring": {},
    "backup": {},
    "cloudflare": {},
    "secrets": {}
}

for layer in layers:
    (root / layer).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "factory_version": "3.0",
    "status": "deployment_ready",
    "generated": datetime.utcnow().isoformat(),
    "capabilities": list(layers.keys())
}

(root / "DEPLOYMENT_PLANE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Deployment Plane Generated: {product}")

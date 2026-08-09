from pathlib import Path
import json
from datetime import datetime
import sys

if len(sys.argv) < 2:
    print("Usage: python3 api_mesh_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "api_integration_mesh"

layers = {
    "gateway": {},
    "services": {},
    "connectors": {},
    "event_bus": {},
    "webhooks": {},
    "governance": {},
    "monitoring": {},
    "intelligence": {}
}

for layer in layers:
    (root / layer).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "factory_version": "3.9",
    "status": "api_mesh_ready",
    "generated": datetime.utcnow().isoformat(),
    "components": list(layers.keys())
}

(root / "API_INTEGRATION_MESH_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS API Integration Mesh Generated: {product}")

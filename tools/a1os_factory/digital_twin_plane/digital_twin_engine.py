from pathlib import Path
import json
from datetime import datetime
import sys

if len(sys.argv) < 2:
    print("Usage: python3 digital_twin_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "digital_twin"

layers = {
    "models": {},
    "simulation": {},
    "scenarios": {},
    "forecasting": {},
    "optimization": {},
    "learning": {}
}

for layer in layers:
    (root / layer).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "factory_version": "3.5",
    "status": "digital_twin_ready",
    "generated": datetime.utcnow().isoformat(),
    "components": list(layers.keys())
}

(root / "DIGITAL_TWIN_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Digital Twin Plane Generated: {product}")

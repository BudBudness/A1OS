from pathlib import Path
import json
from datetime import datetime
import sys

if len(sys.argv) < 2:
    print("Usage: python3 self_improvement_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "self_improvement"

layers = {
    "analysis": {},
    "recommendations": {},
    "optimizations": {},
    "upgrades": {},
    "history": {},
    "governance": {}
}

for layer in layers:
    (root / layer).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "factory_version": "3.6",
    "status": "self_improvement_ready",
    "generated": datetime.utcnow().isoformat(),
    "capabilities": list(layers.keys())
}

(root / "SELF_IMPROVEMENT_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Self-Improvement Plane Generated: {product}")

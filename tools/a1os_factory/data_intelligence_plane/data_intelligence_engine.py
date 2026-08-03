from pathlib import Path
import json
from datetime import datetime
import sys

if len(sys.argv) < 2:
    print("Usage: python3 data_intelligence_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "data_intelligence"

layers = {
    "models": {},
    "warehouse": {},
    "pipelines": {},
    "analytics": {},
    "reports": {},
    "ai_insights": {},
    "governance": {}
}

for layer in layers:
    (root / layer).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "factory_version": "3.3",
    "status": "data_intelligence_ready",
    "generated": datetime.utcnow().isoformat(),
    "capabilities": list(layers.keys())
}

(root / "DATA_INTELLIGENCE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Data Intelligence Plane Generated: {product}")

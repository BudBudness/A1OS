from pathlib import Path
import yaml
import json
import sys
from datetime import datetime

ROOT = Path("products")
CONFIG = Path("tools/a1os_factory/intelligence_runtime/intelligence_manifest.yaml")

if len(sys.argv) < 3:
    print("Usage: python3 intelligence_generator.py product-name profile")
    sys.exit(1)

name = sys.argv[1]
profile = sys.argv[2]

config = yaml.safe_load(CONFIG.read_text())

if profile not in config["intelligence"]:
    print("Unknown intelligence profile")
    sys.exit(1)

product = ROOT / name

if not product.exists():
    print("Product does not exist")
    sys.exit(1)

intel = product / "intelligence_runtime"

profile_data = config["intelligence"][profile]

for category, items in profile_data.items():
    for item in items:
        path = intel / category / item
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("")

manifest = {
    "product": name,
    "profile": profile,
    "factory_version": config["factory"]["version"],
    "agents": profile_data["agents"],
    "workflows": profile_data["workflows"],
    "analytics": profile_data["analytics"],
    "generated": datetime.utcnow().isoformat(),
    "status": "intelligence_ready"
}

(intel / "INTELLIGENCE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Intelligence Runtime Injected: {product}")

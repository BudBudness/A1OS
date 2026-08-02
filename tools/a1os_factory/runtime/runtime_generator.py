from pathlib import Path
import yaml
import json
import sys
from datetime import datetime

ROOT = Path("products")
CONFIG = Path("tools/a1os_factory/runtime/runtime_manifest.yaml")

if len(sys.argv) < 2:
    print("Usage: python3 runtime_generator.py product-name")
    sys.exit(1)

name = sys.argv[1]

config = yaml.safe_load(CONFIG.read_text())

product = ROOT / name

if not product.exists():
    print("Product does not exist. Generate DNA first.")
    sys.exit(1)

runtime = product / "runtime"

layers = {
    "database": [
        "schema.sql",
        "migrations"
    ],
    "api": [
        "routers",
        "services",
        "models"
    ],
    "security": [
        "roles",
        "permissions",
        "audit"
    ],
    "web": [
        "dashboards",
        "components"
    ],
    "deployment": [
        "docker",
        "environment",
        "health_checks"
    ],
    "tests": [
        "api_tests",
        "integration_tests"
    ]
}

for layer, items in layers.items():
    for item in items:
        path = runtime / layer / item
        if "." in item:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("")
        else:
            path.mkdir(parents=True, exist_ok=True)

manifest = {
    "product": name,
    "factory_version": config["factory"]["version"],
    "runtime_generated": True,
    "generated": datetime.utcnow().isoformat(),
    "layers": list(layers.keys())
}

(runtime / "RUNTIME_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Runtime Generated: {product}")

from pathlib import Path
import yaml
import sys
import json
from datetime import datetime

ROOT = Path("products")
CONFIG = Path("tools/a1os_factory/composer/composer_manifest.yaml")

if len(sys.argv) < 3:
    print("Usage: python3 product_composer.py <product-name> <profile>")
    sys.exit(1)

name = sys.argv[1]
profile = sys.argv[2]

config = yaml.safe_load(CONFIG.read_text())

if profile not in config["profiles"]:
    print("Unknown profile")
    sys.exit(1)

product = ROOT / name
dna = config["profiles"][profile]

layers = [
    "core",
    "intelligence",
    "api",
    "web",
    "deployments",
    "docs"
]

for layer in layers:
    (product / layer).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": name,
    "profile": profile,
    "factory_version": config["factory"]["version"],
    "created": datetime.utcnow().isoformat(),
    "base": dna["base"],
    "intelligence_modules": dna["intelligence"],
    "status": "generated"
}

(product / "A1OS_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Autonomous Product Created: {product}")

from pathlib import Path
import yaml
import sys
import json

ROOT = Path("products")

FACTORY = Path("tools/a1os_factory/factory_config.yaml")
MANIFEST = Path("tools/a1os_factory/product_manifest.yaml")

if len(sys.argv) < 2:
    print("Usage: python3 generate_product.py <product-name>")
    sys.exit(1)

name = sys.argv[1]

config = yaml.safe_load(FACTORY.read_text())
manifest = yaml.safe_load(MANIFEST.read_text())

product = ROOT / name

layers = manifest.get(
    "layers",
    config["defaults"]["environment"]
)

modules = manifest.get(
    "modules",
    []
)

for layer in layers:
    (product / layer).mkdir(
        parents=True,
        exist_ok=True
    )

for module in modules:
    (product / "core" / module).mkdir(
        parents=True,
        exist_ok=True
    )

metadata = {
    "product": name,
    "factory": config["factory"]["name"],
    "factory_version": config["factory"]["version"],
    "modules": modules,
    "status": "generated"
}

(product / "A1OS_PRODUCT.json").write_text(
    json.dumps(metadata, indent=2)
)

print(
    f"A1OS Factory generated product: {name}"
)

from pathlib import Path
import yaml
import sys

ROOT = Path("products")

if len(sys.argv) < 2:
    print("Usage: python3 generate_product.py product-name")
    sys.exit(1)

name = sys.argv[1]
manifest = yaml.safe_load(
    Path("tools/a1os_factory/product_manifest.yaml").read_text()
)

product = ROOT / name

for layer in manifest["layers"]:
    (product / layer).mkdir(parents=True, exist_ok=True)

(product / "MANIFEST.yaml").write_text(
    yaml.dump({
        "product": name,
        "version": manifest["version"],
        "modules": manifest["modules"]
    })
)

print(f"A1OS product generated: {product}")

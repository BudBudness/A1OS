from pathlib import Path
import json
import sys
from datetime import datetime

ROOT = Path("products")

registry = []

for product in ROOT.iterdir():
    if product.is_dir() and not product.name.startswith("."):
        manifest = {}

        files = list(product.glob("*MANIFEST*"))

        if files:
            try:
                manifest = json.loads(files[0].read_text())
            except Exception:
                manifest = {}

        registry.append({
            "product": product.name,
            "profile": manifest.get("profile", "unknown"),
            "version": manifest.get("factory_version", "unknown"),
            "status": manifest.get("status", "registered"),
            "layers": [
                x.name for x in product.iterdir()
                if x.is_dir()
            ]
        })

output = {
    "factory_version": "2.1",
    "generated": datetime.utcnow().isoformat(),
    "products_registered": len(registry),
    "products": registry,
    "registry_status": "active"
}

registry_dir = Path("factory_registry")
registry_dir.mkdir(exist_ok=True)

(registry_dir / "PRODUCT_REGISTRY.json").write_text(
    json.dumps(output, indent=2)
)

print("A1OS Product Registry Generated")
print(f"Products: {len(registry)}")

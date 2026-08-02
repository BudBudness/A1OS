from pathlib import Path
import json
import sys
from datetime import datetime

ROOT = Path("products")

if len(sys.argv) < 2:
    print("Usage: python3 evolution_engine.py product-name")
    sys.exit(1)

name = sys.argv[1]

product = ROOT / name

if not product.exists():
    print("Product does not exist")
    sys.exit(1)

manifest_files = list(product.glob("**/*MANIFEST*"))

changes = []
modules = []

for item in product.iterdir():
    if item.is_dir():
        modules.append(item.name)

if not manifest_files:
    changes.append("initial-baseline-created")

upgrade = {
    "product": name,
    "factory_version": "1.9",
    "generated": datetime.utcnow().isoformat(),
    "detected_modules": modules,
    "changes": changes,
    "migration_plan": [
        "validate_current_state",
        "apply_module_updates",
        "verify_integrity",
        "generate_release_report"
    ],
    "rollback": {
        "enabled": True,
        "strategy": "restore_previous_manifest"
    },
    "status": "upgrade_ready"
}

evolution = product / "evolution"
evolution.mkdir(exist_ok=True)

(evolution / "UPGRADE_MANIFEST.json").write_text(
    json.dumps(upgrade, indent=2)
)

print(f"A1OS Evolution Analysis Complete: {product}")
print(upgrade["status"])

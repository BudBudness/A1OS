from pathlib import Path
import yaml
import json
import sys
from datetime import datetime

ROOT = Path("products")
CONFIG = Path("tools/a1os_factory/operations/operations_manifest.yaml")

if len(sys.argv) < 2:
    print("Usage: python3 operations_generator.py product-name")
    sys.exit(1)

name = sys.argv[1]

config = yaml.safe_load(CONFIG.read_text())

product = ROOT / name

if not product.exists():
    print("Product does not exist")
    sys.exit(1)

operations = product / "operations"

structure = {
    "deployment": [
        "docker",
        "compose",
        "environments",
        "secrets_template"
    ],
    "cicd": [
        "github_actions",
        "build_pipeline",
        "test_pipeline",
        "release_pipeline"
    ],
    "monitoring": [
        "health_checks",
        "metrics",
        "logging",
        "alerts"
    ],
    "recovery": [
        "backup_jobs",
        "restore_jobs",
        "disaster_recovery"
    ],
    "production": [
        "readiness",
        "security_checks",
        "deployment_manifest"
    ]
}

for layer, items in structure.items():
    for item in items:
        path = operations / layer / item
        path.parent.mkdir(parents=True, exist_ok=True)

        if "." not in item:
            path.mkdir(parents=True, exist_ok=True)
        else:
            path.write_text("")

manifest = {
    "product": name,
    "factory_version": config["factory"]["version"],
    "operations_ready": True,
    "generated": datetime.utcnow().isoformat(),
    "layers": list(structure.keys()),
    "status": "production_ready"
}

(operations / "OPERATIONS_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Operations Runtime Generated: {product}")

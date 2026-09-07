import json
from pathlib import Path
from datetime import datetime, timezone
import sys

product = sys.argv[1] if len(sys.argv) > 1 else "unknown-product"

root = Path("factory_runs") / product / "generated_artifacts"

artifacts = {
    "backend": {
        "directories": [
            "api",
            "services",
            "models",
            "controllers",
            "workers"
        ]
    },
    "frontend": {
        "directories": [
            "dashboard",
            "components",
            "pages",
            "assets"
        ]
    },
    "database": {
        "directories": [
            "migrations",
            "schemas",
            "seeds"
        ]
    },
    "security": {
        "directories": [
            "auth",
            "policies",
            "audit"
        ]
    },
    "deployment": {
        "directories": [
            "docker",
            "kubernetes",
            "terraform",
            "ansible"
        ]
    },
    "testing": {
        "directories": [
            "unit",
            "integration",
            "e2e"
        ]
    }
}

for category, config in artifacts.items():
    for folder in config["directories"]:
        (root / category / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "plane": "artifact_generation_engine",
    "version": "8.1",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "product": product,
    "status": "artifact_generation_complete",
    "artifact_categories": list(artifacts.keys()),
    "generated_path": str(root),
    "capabilities": [
        "backend_scaffolding",
        "frontend_scaffolding",
        "database_layout_generation",
        "security_structure_generation",
        "deployment_structure_generation",
        "testing_structure_generation"
    ]
}

(root / "ARTIFACT_GENERATION_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print("=" * 70)
print("A1OS FACTORY ARTIFACT GENERATION ENGINE v8.1")
print("=" * 70)
print(f"Product: {product}")
print("Artifacts generated:")
for item in artifacts:
    print(f" ✓ {item}")

print(f"\nManifest:")
print(root / "ARTIFACT_GENERATION_MANIFEST.json")

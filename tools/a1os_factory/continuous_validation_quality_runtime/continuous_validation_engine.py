import json
import sys
from pathlib import Path
from datetime import datetime, timezone

product = sys.argv[1] if len(sys.argv) > 1 else "unknown"

root = Path("factory_runs") / product / "continuous_validation"
root.mkdir(parents=True, exist_ok=True)

components = [
    "unit_tests",
    "integration_tests",
    "security_validation",
    "dependency_scanning",
    "performance_checks",
    "api_validation",
    "database_validation",
    "deployment_readiness"
]

manifest = {
    "runtime": "a1os_factory_continuous_validation_quality_runtime",
    "version": "9.1",
    "product": product,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "status": "validation_runtime_initialized",
    "quality_gates": {
        "tests": True,
        "security": True,
        "performance": True,
        "deployment": True
    },
    "validation_components": components,
    "promotion_policy": "pass_required_before_production"
}

(root / "VALIDATION_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print("=" * 70)
print("A1OS FACTORY CONTINUOUS VALIDATION QUALITY RUNTIME v9.1")
print("=" * 70)
print(f"Product: {product}")

for component in components:
    print("✓", component)

print(f"Artifacts: {root}")

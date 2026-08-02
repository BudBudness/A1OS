import json
from pathlib import Path
from datetime import datetime, timezone
import sys

product = sys.argv[1] if len(sys.argv) > 1 else "unknown-product"

root = Path("factory_runs") / product / "deployment_runtime"

folders = [
    "environments",
    "releases",
    "rollouts",
    "health_checks",
    "rollback_history",
    "deployment_logs"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "plane": "autonomous_deployment_runtime",
    "version": "8.3",
    "product": product,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "status": "deployment_runtime_initialized",
    "capabilities": [
        "environment_management",
        "deployment_planning",
        "release_tracking",
        "health_validation",
        "rollback_management",
        "deployment_audit"
    ],
    "folders": folders
}

(root / "DEPLOYMENT_RUNTIME_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print("=" * 70)
print("A1OS FACTORY AUTONOMOUS DEPLOYMENT RUNTIME v8.3")
print("=" * 70)
print(f"Product: {product}")
print("Deployment lifecycle initialized")

for item in folders:
    print(" ✓", item)

print(root)

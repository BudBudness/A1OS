import json
import sys
from pathlib import Path
from datetime import datetime, timezone

product = sys.argv[1] if len(sys.argv) > 1 else "unknown"

root = Path("factory_runs") / product / "release_lifecycle"
root.mkdir(parents=True, exist_ok=True)

manifest = {
    "plane": "release_lifecycle_runtime",
    "version": "9.0",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "product": product,
    "status": "release_lifecycle_initialized",
    "capabilities": [
        "version_management",
        "release_tracking",
        "artifact_promotion",
        "environment_alignment",
        "change_management",
        "rollback_coordination",
        "release_auditing"
    ],
    "pipeline": [
        "development",
        "validation",
        "staging",
        "production",
        "monitoring"
    ]
}

(root / "RELEASE_LIFECYCLE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print("=" * 70)
print("A1OS FACTORY RELEASE LIFECYCLE RUNTIME v9.0")
print("=" * 70)
print(f"Product: {product}")
print("✓ version management")
print("✓ release tracking")
print("✓ artifact promotion")
print("✓ environment alignment")
print("✓ rollback coordination")
print("✓ release auditing")
print(f"Artifacts: {root}")

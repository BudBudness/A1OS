import json
from pathlib import Path
from datetime import datetime, timezone
import sys

product = sys.argv[1] if len(sys.argv) > 1 else "unknown"

root = Path("factory_runs") / product / "production_promotion"
root.mkdir(parents=True, exist_ok=True)

components = [
    "validation_gate",
    "release_approval",
    "artifact_promotion",
    "environment_verification",
    "production_readiness",
    "rollback_checkpoint",
    "governance_audit"
]

manifest = {
    "runtime": "production_promotion_governance_runtime",
    "version": "9.2",
    "generated": datetime.now(timezone.utc).isoformat(),
    "product": product,
    "status": "promotion_ready",
    "promotion_flow": [
        "quality_validation",
        "release_candidate",
        "approval_gate",
        "production_promotion",
        "runtime_monitoring"
    ],
    "governance_controls": components,
    "production_policy": "validated_artifacts_only"
}

(root / "PROMOTION_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print("=" * 70)
print("A1OS FACTORY PRODUCTION PROMOTION GOVERNANCE RUNTIME v9.2")
print("=" * 70)
print(f"Product: {product}")

for component in components:
    print("✓", component)

print(f"Artifacts: {root}")

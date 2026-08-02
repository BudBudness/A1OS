import json
import sys
from pathlib import Path
from datetime import datetime, timezone

if len(sys.argv) < 2:
    print("Usage: python3 product_lifecycle_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "product_lifecycle"

folders = [
    "planning",
    "roadmaps",
    "requirements",
    "releases",
    "versions",
    "experiments",
    "feedback",
    "deprecation",
    "innovation"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "plane": "product_lifecycle_management",
    "version": "5.1",
    "generated": datetime.now(timezone.utc).isoformat(),
    "status": "lifecycle_ready",
    "capabilities": [
        "product_planning",
        "roadmap_management",
        "release_orchestration",
        "version_control",
        "feature_tracking",
        "customer_feedback_intelligence",
        "innovation_management",
        "product_evolution"
    ]
}

(root / "PRODUCT_LIFECYCLE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Product Lifecycle Plane Generated: {product}")

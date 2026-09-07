import json
import sys
from pathlib import Path
from datetime import datetime, timezone

if len(sys.argv) < 2:
    print("Usage: python3 customer_success_intelligence_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "customer_success"

folders = [
    "customer_profiles",
    "adoption_tracking",
    "health_scores",
    "support_intelligence",
    "success_playbooks",
    "renewals",
    "expansion",
    "feedback_loops",
    "customer_analytics"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "plane": "customer_success_lifecycle_intelligence",
    "version": "6.3",
    "generated": datetime.now(timezone.utc).isoformat(),
    "status": "customer_success_ready",
    "capabilities": [
        "customer_health_scoring",
        "adoption_intelligence",
        "support_automation",
        "renewal_forecasting",
        "expansion_intelligence",
        "feedback_analysis",
        "customer_lifecycle_management"
    ]
}

(root / "CUSTOMER_SUCCESS_INTELLIGENCE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Customer Success Intelligence Plane Generated: {product}")

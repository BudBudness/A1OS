import json
import sys
from pathlib import Path
from datetime import datetime, timezone

if len(sys.argv) < 2:
    print("Usage: python3 ai_governance_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "ai_governance"

folders = [
    "policies",
    "model_registry",
    "evaluations",
    "risk_assessments",
    "approvals",
    "audit",
    "transparency",
    "monitoring",
    "reporting"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "plane": "ai_governance",
    "version": "5.2",
    "generated": datetime.now(timezone.utc).isoformat(),
    "status": "ai_governance_ready",
    "capabilities": [
        "model_governance",
        "responsible_ai",
        "ai_risk_management",
        "human_oversight",
        "governance_intelligence"
    ]
}

(root / "AI_GOVERNANCE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS AI Governance Plane Generated: {product}")

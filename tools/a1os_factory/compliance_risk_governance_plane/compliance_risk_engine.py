import json
import sys
from pathlib import Path
from datetime import datetime, timezone

if len(sys.argv) < 2:
    print("Usage: python3 compliance_risk_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "compliance_governance"

folders = [
    "policies",
    "controls",
    "frameworks",
    "risk_models",
    "assessments",
    "evidence",
    "audits",
    "governance",
    "reporting"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "plane": "compliance_risk_governance",
    "version": "4.7",
    "generated": datetime.now(timezone.utc).isoformat(),
    "status": "governance_ready",
    "capabilities": [
        "compliance_mapping",
        "risk_management",
        "policy_automation",
        "audit_readiness",
        "governance_intelligence"
    ]
}

(root / "COMPLIANCE_RISK_GOVERNANCE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Compliance Risk Governance Plane Generated: {product}")

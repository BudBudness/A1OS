import json
import sys
from pathlib import Path
from datetime import datetime, timezone

if len(sys.argv) < 2:
    print("Usage: python3 enterprise_command_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "enterprise_command"

folders = [
    "executive_dashboard",
    "portfolio_intelligence",
    "strategic_kpis",
    "decision_intelligence",
    "business_intelligence",
    "governance",
    "reporting",
    "ai_assistant",
    "operations_center"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "plane": "enterprise_command_control",
    "version": "5.0",
    "generated": datetime.now(timezone.utc).isoformat(),
    "status": "enterprise_command_ready",
    "capabilities": [
        "executive_dashboard",
        "portfolio_intelligence",
        "strategic_kpi_management",
        "decision_support",
        "business_intelligence",
        "enterprise_governance",
        "ai_executive_assistant",
        "operations_command_center"
    ]
}

(root / "ENTERPRISE_COMMAND_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Enterprise Command Plane Generated: {product}")

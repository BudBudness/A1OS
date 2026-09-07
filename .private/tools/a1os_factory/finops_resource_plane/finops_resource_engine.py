import json
import sys
from pathlib import Path
from datetime import datetime, timezone

if len(sys.argv) < 2:
    print("Usage: python3 finops_resource_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "finops_resource"

folders = [
    "cost_tracking",
    "budgets",
    "forecasting",
    "optimization",
    "utilization",
    "anomalies",
    "roi_models",
    "governance",
    "reporting"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "plane": "finops_resource_optimization",
    "version": "4.9",
    "generated": datetime.now(timezone.utc).isoformat(),
    "status": "finops_ready",
    "capabilities": [
        "cost_intelligence",
        "resource_optimization",
        "financial_governance",
        "forecasting",
        "roi_analysis"
    ]
}

(root / "FINOPS_RESOURCE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS FinOps Resource Plane Generated: {product}")

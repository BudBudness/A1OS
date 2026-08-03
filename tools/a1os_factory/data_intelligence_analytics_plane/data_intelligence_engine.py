import json
import sys
from pathlib import Path
from datetime import datetime, timezone

if len(sys.argv) < 2:
    print("Usage: python3 data_intelligence_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "data_intelligence"

folders = [
    "data_lake",
    "pipelines",
    "warehouse",
    "analytics",
    "metrics",
    "dashboards",
    "quality",
    "governance",
    "ai_readiness",
    "insights"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "plane": "data_intelligence_analytics",
    "version": "5.5",
    "generated": datetime.now(timezone.utc).isoformat(),
    "status": "data_intelligence_ready",
    "capabilities": [
        "data_lake_foundations",
        "data_pipeline_automation",
        "analytics_intelligence",
        "metrics_management",
        "data_quality_monitoring",
        "ai_data_readiness",
        "business_insights"
    ]
}

(root / "DATA_INTELLIGENCE_ANALYTICS_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Data Intelligence Analytics Plane Generated: {product}")

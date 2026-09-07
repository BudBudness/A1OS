import json
import sys
from pathlib import Path
from datetime import datetime, timezone

product = sys.argv[1] if len(sys.argv) > 1 else "unknown"

root = Path("products") / product / "observability_reliability"

folders = [
    "telemetry",
    "metrics",
    "logs",
    "traces",
    "alerts",
    "incidents",
    "health_models",
    "dashboards",
    "reliability"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "plane": "observability_reliability",
    "version": "4.5",
    "generated": datetime.now(timezone.utc).isoformat(),
    "capabilities": [
        "telemetry",
        "monitoring",
        "alerting",
        "incident_management",
        "reliability_engineering",
        "self_healing"
    ]
}

(root / "OBSERVABILITY_RELIABILITY_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Observability Reliability Plane Generated: {product}")

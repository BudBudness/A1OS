import json
import sys
from pathlib import Path
from datetime import datetime, timezone

if len(sys.argv) < 2:
    print("Usage: python3 secops_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "secops"

folders = [
    "threat_intelligence",
    "security_events",
    "detection_rules",
    "incident_response",
    "playbooks",
    "vulnerability_management",
    "forensics",
    "posture_monitoring",
    "analytics"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "plane": "security_operations_center",
    "version": "4.8",
    "generated": datetime.now(timezone.utc).isoformat(),
    "status": "secops_ready",
    "capabilities": [
        "threat_intelligence",
        "security_monitoring",
        "incident_response",
        "vulnerability_management",
        "security_analytics"
    ]
}

(root / "SECOPS_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS SecOps Plane Generated: {product}")

import json
from pathlib import Path
from datetime import datetime, timezone
import sys

product = sys.argv[1] if len(sys.argv) > 1 else "unknown-product"

root = Path("factory_runs") / product / "intelligence_command_center"

modules = {
    "dashboard": [
        "executive_dashboard",
        "operations_dashboard"
    ],
    "inventory": [
        "engine_registry",
        "plane_registry"
    ],
    "monitoring": [
        "system_health",
        "runtime_status",
        "deployment_status"
    ],
    "intelligence": [
        "reports",
        "recommendations",
        "decision_history"
    ],
    "commands": [
        "operator_actions",
        "automation_controls"
    ]
}

for group, items in modules.items():
    for item in items:
        (root / group / item).mkdir(parents=True, exist_ok=True)

manifest = {
    "plane": "factory_intelligence_command_center",
    "version": "8.9",
    "product": product,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "status": "command_center_initialized",
    "capabilities": [
        "executive_visibility",
        "runtime_monitoring",
        "system_health_scoring",
        "intelligence_reporting",
        "operator_control"
    ],
    "modules": modules
}

(root / "COMMAND_CENTER_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print("=" * 70)
print("A1OS FACTORY INTELLIGENCE COMMAND CENTER v8.9")
print("=" * 70)
print(f"Product: {product}")

for module in modules:
    print("✓", module)

print(root)

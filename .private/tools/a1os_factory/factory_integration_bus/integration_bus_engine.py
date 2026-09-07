import json
from pathlib import Path
from datetime import datetime, timezone
import sys

product = sys.argv[1] if len(sys.argv) > 1 else "unknown-product"

root = Path("factory_runs") / product / "integration_bus"

components = {
    "events": [
        "deployment_events",
        "security_events",
        "agent_events",
        "data_events"
    ],
    "api_gateway": [
        "internal_routes",
        "service_registry"
    ],
    "workflow_triggers": [
        "automation_rules",
        "execution_hooks"
    ],
    "messaging": [
        "agent_messages",
        "system_messages"
    ],
    "audit": [
        "event_history",
        "integration_logs"
    ]
}

for group, items in components.items():
    for item in items:
        (root / group / item).mkdir(parents=True, exist_ok=True)

manifest = {
    "plane": "factory_integration_bus",
    "version": "8.8",
    "product": product,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "status": "integration_initialized",
    "capabilities": [
        "event_routing",
        "api_integration",
        "workflow_triggering",
        "agent_communication",
        "audit_tracking"
    ],
    "components": components
}

(root / "INTEGRATION_BUS_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print("=" * 70)
print("A1OS FACTORY INTEGRATION BUS v8.8")
print("=" * 70)
print(f"Product: {product}")

for component in components:
    print("✓", component)

print(root)

import json
from pathlib import Path
from datetime import datetime, timezone
import sys

product = sys.argv[1] if len(sys.argv) > 1 else "unknown-product"

root = Path("factory_runs") / product / "agent_operations"

components = {
    "agent_registry": [
        "agents.json",
        "capabilities.json"
    ],
    "task_orchestration": [
        "task_queue",
        "execution_plans"
    ],
    "memory": [
        "agent_memory",
        "knowledge_context"
    ],
    "operations": [
        "monitoring_agents",
        "remediation_agents",
        "optimization_agents"
    ],
    "verification": [
        "agent_logs",
        "execution_reports"
    ]
}

for group, items in components.items():
    for item in items:
        path = root / group / item
        path.mkdir(parents=True, exist_ok=True) if "." not in item else path.write_text(
            json.dumps(
                {
                    "created": datetime.now(timezone.utc).isoformat(),
                    "status": "initialized"
                },
                indent=2
            )
        )

manifest = {
    "plane": "autonomous_agent_operations_runtime",
    "version": "8.7",
    "product": product,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "status": "initialized",
    "capabilities": [
        "agent_management",
        "task_execution",
        "agent_memory",
        "autonomous_monitoring",
        "self_remediation",
        "optimization"
    ],
    "components": components
}

(root / "AGENT_OPERATIONS_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print("=" * 70)
print("A1OS FACTORY AUTONOMOUS AGENT OPERATIONS RUNTIME v8.7")
print("=" * 70)
print(f"Product: {product}")

for component in components:
    print("✓", component)

print(root)

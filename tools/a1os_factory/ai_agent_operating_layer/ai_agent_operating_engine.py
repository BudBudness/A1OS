import json
from pathlib import Path
from datetime import datetime, timezone

root = Path("tools/a1os_factory/ai_agent_operating_layer")

folders = [
    "agents",
    "memory",
    "tasks",
    "planning",
    "tools",
    "execution",
    "verification",
    "learning",
    "governance"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "plane": "ai_agent_operating_layer",
    "version": "7.6",
    "generated": datetime.now(timezone.utc).isoformat(),
    "status": "agent_runtime_initialized",
    "capabilities": [
        "agent_registry",
        "agent_lifecycle_management",
        "task_planning",
        "memory_management",
        "tool_assignment",
        "execution_loops",
        "verification",
        "continuous_improvement"
    ],
    "subsystems": folders
}

(root / "AI_AGENT_OPERATING_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print("A1OS AI Agent Operating Layer v7.6 Ready")

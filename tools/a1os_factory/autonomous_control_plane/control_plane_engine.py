import json
from pathlib import Path
from datetime import datetime, timezone

root = Path("tools/a1os_factory/autonomous_control_plane")

folders = [
    "orchestration",
    "jobs",
    "state",
    "workflows",
    "engine_graph",
    "audit",
    "monitoring",
    "operators"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

engines = sorted(
    Path("tools/a1os_factory").rglob("*engine.py")
)

manifest = {
    "plane": "autonomous_control_plane",
    "version": "7.5",
    "generated": datetime.now(timezone.utc).isoformat(),
    "status": "control_plane_initialized",
    "connected_engines": len(engines),
    "capabilities": [
        "engine_orchestration",
        "workflow_coordination",
        "job_management",
        "execution_state_tracking",
        "dependency_graph_management",
        "audit_tracking",
        "operator_control"
    ],
    "subsystems": folders
}

(root / "CONTROL_PLANE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print("A1OS Autonomous Control Plane v7.5 Ready")
print(f"Connected engines: {len(engines)}")

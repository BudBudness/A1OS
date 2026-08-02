import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("tools/a1os_factory")

if len(sys.argv) < 2:
    print("Usage: python3 factory_runtime.py product-name")
    sys.exit(1)

product = sys.argv[1]

roadmap = Path("IMPLEMENTATION_ROADMAP.json")

if not roadmap.exists():
    print("Missing IMPLEMENTATION_ROADMAP.json")
    sys.exit(1)

data = json.loads(roadmap.read_text())

runtime = Path("products") / product / "factory_runtime"

folders = [
    "generated",
    "artifacts",
    "logs",
    "executions",
    "reports"
]

for folder in folders:
    (runtime / folder).mkdir(parents=True, exist_ok=True)

execution = {
    "product": product,
    "runtime": "a1os_factory_runtime_core",
    "version": "7.0",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "engines_discovered": data["engines"],
    "total_engines": len(data["roadmap"]),
    "status": "runtime_initialized",
    "next_stage": [
        "engine_adapters",
        "code_generation",
        "deployment_execution",
        "autonomous_orchestration"
    ]
}

(runtime / "RUNTIME_EXECUTION_MANIFEST.json").write_text(
    json.dumps(execution, indent=2)
)

print("A1OS Factory Runtime Core Initialized")
print(f"Product: {product}")
print(f"Engines connected: {len(data['roadmap'])}")

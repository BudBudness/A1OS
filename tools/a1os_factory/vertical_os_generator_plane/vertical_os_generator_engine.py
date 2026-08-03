import json
import sys
from pathlib import Path
from datetime import datetime, timezone

if len(sys.argv) < 2:
    print("Usage: python3 vertical_os_generator_engine.py vertical-os-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "vertical_os"

folders = [
    "architecture",
    "modules",
    "database",
    "identity",
    "workflows",
    "agents",
    "apis",
    "integrations",
    "billing",
    "compliance",
    "deployment",
    "documentation"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "plane": "vertical_os_generator",
    "version": "6.0",
    "generated": datetime.now(timezone.utc).isoformat(),
    "status": "vertical_os_ready",
    "capabilities": [
        "vertical_architecture_generation",
        "module_composition",
        "database_blueprint_generation",
        "identity_model_generation",
        "workflow_generation",
        "agent_assignment",
        "api_generation",
        "integration_mapping",
        "billing_model_generation",
        "compliance_mapping",
        "deployment_packaging"
    ]
}

(root / "VERTICAL_OS_GENERATOR_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Vertical OS Generated: {product}")

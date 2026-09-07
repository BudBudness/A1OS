import json
import sys
from pathlib import Path
from datetime import datetime, timezone

if len(sys.argv) < 2:
    print("Usage: python3 service_mesh_platform_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "service_mesh_platform"

folders = [
    "service_registry",
    "service_discovery",
    "platform_apis",
    "runtime_orchestration",
    "deployment_coordination",
    "environment_promotion",
    "developer_portal",
    "golden_paths",
    "engineering_intelligence"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "plane": "service_mesh_platform_engineering",
    "version": "5.4",
    "generated": datetime.now(timezone.utc).isoformat(),
    "status": "platform_ready",
    "capabilities": [
        "service_registry",
        "service_discovery",
        "platform_api_management",
        "runtime_orchestration",
        "deployment_coordination",
        "developer_self_service",
        "engineering_intelligence"
    ]
}

(root / "SERVICE_MESH_PLATFORM_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Service Mesh Platform Plane Generated: {product}")

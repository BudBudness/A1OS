import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("tools/a1os_factory")

engines = sorted(ROOT.rglob("*engine.py"))

generator = Path("tools/a1os_factory/code_generation_pipeline")

artifacts = [
    "backend",
    "frontend",
    "database",
    "api",
    "authentication",
    "testing",
    "documentation",
    "deployment"
]

manifest = {
    "plane": "code_generation_pipeline",
    "version": "7.2",
    "generated": datetime.now(timezone.utc).isoformat(),
    "status": "code_generation_ready",
    "connected_engines": len(engines),
    "artifact_targets": artifacts,
    "capabilities": [
        "template_generation",
        "application_scaffolding",
        "api_generation",
        "database_generation",
        "test_generation",
        "deployment_artifact_generation"
    ]
}

(generator / "CODE_GENERATION_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print("A1OS Code Generation Pipeline v7.2 Ready")
print(f"Connected factory engines: {len(engines)}")

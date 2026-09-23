"""Deterministic code-generation manifest pipeline."""
from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ENGINE_ROOT = Path("tools/a1os_factory")
TARGETS = ("frontend", "workflows", "forms", "integrations", "tests", "documentation", "deployment-contract")

def generate(product: str, requirements: dict, output: Path | None = None) -> dict:
    requested = set(requirements.get("artifacts", TARGETS))
    artifacts = [item for item in TARGETS if item in requested]
    manifest = {
        "plane": "code_generation_pipeline",
        "version": "2.0",
        "product": product,
        "generated": datetime.now(timezone.utc).isoformat(),
        "status": "ready",
        "customized": True,
        "artifact_targets": artifacts,
        "requirements": requirements,
        "engine_count": len(list(ENGINE_ROOT.rglob("*_engine.py"))),
    }
    destination = output or Path("factory_runs") / product / "CODE_GENERATION_MANIFEST.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 code_generation_engine.py PRODUCT REQUIREMENTS_JSON")
        raise SystemExit(2)
    result = generate(sys.argv[1], json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2))

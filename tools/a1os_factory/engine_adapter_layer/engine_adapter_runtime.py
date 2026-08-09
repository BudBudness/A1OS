import json
import importlib.util
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("tools/a1os_factory")

engines = sorted(ROOT.rglob("*engine.py"))

adapters = []

for engine in engines:
    adapters.append({
        "engine": str(engine),
        "name": engine.stem,
        "status": "adapter_registered",
        "registered": datetime.now(timezone.utc).isoformat()
    })

manifest = {
    "runtime": "a1os_engine_adapter_layer",
    "version": "7.1",
    "total_engines": len(adapters),
    "status": "engine_registry_ready",
    "engines": adapters,
    "capabilities": [
        "engine_discovery",
        "engine_registration",
        "execution_hooks",
        "output_collection",
        "runtime_integration"
    ]
}

Path("tools/a1os_factory/engine_adapter_layer/ENGINE_ADAPTER_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print("A1OS Engine Adapter Layer v7.1 Ready")
print(f"Registered engines: {len(adapters)}")

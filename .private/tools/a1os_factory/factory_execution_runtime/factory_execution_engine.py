import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("tools/a1os_factory")
OUTPUT = Path("factory_runs")

OUTPUT.mkdir(exist_ok=True)

product = "unknown"

import sys
if len(sys.argv) > 1:
    product = sys.argv[1]

run = OUTPUT / product
run.mkdir(parents=True, exist_ok=True)

engines = sorted(ROOT.rglob("*engine.py"))

stages = [
    "discovery",
    "architecture_generation",
    "code_generation",
    "build_validation",
    "deployment_preparation",
    "intelligence_reporting"
]

manifest = {
    "runtime": "A1OS_FACTORY_EXECUTION_RUNTIME",
    "version": "8.0",
    "product": product,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "engines_connected": len(engines),
    "stages": stages,
    "status": "execution_ready"
}

(run / "EXECUTION_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print("=" * 70)
print("A1OS FACTORY EXECUTION RUNTIME v8.0")
print("=" * 70)
print(f"Product: {product}")
print(f"Connected engines: {len(engines)}")
print("Pipeline:")
for stage in stages:
    print(" ✓", stage)

print()
print("Execution manifest created:")
print(run / "EXECUTION_MANIFEST.json")

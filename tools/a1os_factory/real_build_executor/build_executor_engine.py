"""Real, lightweight build executor for generated verticals."""
from __future__ import annotations
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

def execute(product: str, root: Path = Path("products")) -> dict:
    target = root / product
    if not target.is_dir():
        raise FileNotFoundError(target)
    commands = [
        [sys.executable, "-m", "compileall", "-q", str(target)],
    ]
    results = []
    for command in commands:
        proc = subprocess.run(command, capture_output=True, text=True, check=False)
        results.append({"command": command, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr})
    ok = all(item["returncode"] == 0 for item in results)
    out = Path("factory_runs") / product
    out.mkdir(parents=True, exist_ok=True)
    manifest = {
        "plane": "real_build_executor",
        "version": "2.0",
        "product": product,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "built" if ok else "failed",
        "checks": results,
        "artifacts": ["compiled-python-bytecode"] if ok else [],
    }
    (out / "BUILD_EXECUTOR_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 build_executor_engine.py PRODUCT", file=sys.stderr)
        raise SystemExit(2)
    result = execute(sys.argv[1])
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "built" else 1)

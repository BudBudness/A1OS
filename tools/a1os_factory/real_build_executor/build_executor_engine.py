"""Scoped build executor for generated frontend verticals."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

def execute(product: str, root: Path = Path("products")) -> dict:
    target = root/product
    if not target.is_dir():
        raise FileNotFoundError(target)
    command=[sys.executable,"-m","compileall","-q",str(target)]
    proc=subprocess.run(command,capture_output=True,text=True,check=False)
    ok=proc.returncode==0
    out=Path("factory_runs")/product
    out.mkdir(parents=True,exist_ok=True)
    manifest={"plane":"real_build_executor","version":"2.1","product":product,
              "timestamp":datetime.now(timezone.utc).isoformat(),"status":"built" if ok else "failed",
              "checks":[{"command":command,"returncode":proc.returncode,"stdout":proc.stdout,"stderr":proc.stderr}],
              "artifacts":["compiled-python-bytecode"] if ok else []}
    (out/"BUILD_EXECUTOR_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    return manifest

if __name__ == "__main__":
    if len(sys.argv)!=2:
        print("Usage: python3 build_executor_engine.py PRODUCT",file=sys.stderr); raise SystemExit(2)
    result=execute(sys.argv[1]); print(json.dumps(result,indent=2)); raise SystemExit(0 if result["status"]=="built" else 1)

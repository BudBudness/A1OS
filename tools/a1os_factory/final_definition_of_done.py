"""System-wide A1OS Factory Definition-of-Done audit."""
from __future__ import annotations
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "tools" / "a1os_factory"
ROADMAP = ROOT / "IMPLEMENTATION_ROADMAP.json"
ENGINES = sorted(FACTORY.rglob("*_engine.py"))
EXPECTED = 37
FORBIDDEN = ("jarvis", "mcp")

def main() -> int:
    findings = []
    if len(ENGINES) != EXPECTED:
        findings.append(f"engine_count:{len(ENGINES)}")
    roadmap = json.loads(ROADMAP.read_text(encoding="utf-8"))
    if roadmap.get("engines") != EXPECTED:
        findings.append("roadmap_engine_count")
    if any(item.get("status") != "IMPLEMENTED" for item in roadmap.get("roadmap", [])):
        findings.append("roadmap_not_implemented")
    source = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in FACTORY.rglob("*.py"))
    lower = source.lower()
    if any(token in lower for token in FORBIDDEN):
        findings.append("forbidden-factory-reference")
    control = (ROOT / "core/control_plane/app.py").read_text(encoding="utf-8", errors="ignore").lower()
    if "jarvis" in control or "bash" in control and "create_subprocess_exec" not in control:
        findings.append("control-plane-forbidden-execution")
    for product in ("little-oaks", "legal", "charity"):
        path = ROOT / "products" / "verticals" / product
        if not path.is_dir():
            findings.append(f"missing-vertical:{product}")
    result = {"status": "PASS" if not findings else "FAIL", "engine_count": len(ENGINES), "expected": EXPECTED, "findings": findings}
    print(json.dumps(result, indent=2))
    return 0 if not findings else 1

if __name__ == "__main__":
    raise SystemExit(main())

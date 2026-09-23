"""System-wide A1OS Product Factory Definition-of-Done audit."""
from __future__ import annotations
import ast, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FACTORY=ROOT/"tools"/"a1os_factory"
ROADMAP=ROOT/"IMPLEMENTATION_ROADMAP.json"
EXPECTED=37

def main()->int:
    findings=[]
    roadmap=json.loads(ROADMAP.read_text(encoding="utf-8"))
    entries=roadmap.get("roadmap",[])
    if roadmap.get("engines") != EXPECTED or len(entries) != EXPECTED:
        findings.append("engine_count")
    seen=set()
    for item in entries:
        path=ROOT/item["engine"]
        if item["engine"] in seen:
            findings.append(f"duplicate-engine:{item['engine']}")
        seen.add(item["engine"])
        if not path.is_file():
            findings.append(f"missing-engine:{item['engine']}")
            continue
        if item.get("status") != "IMPLEMENTED":
            findings.append(f"unimplemented:{item['engine']}")
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            findings.append(f"syntax:{item['engine']}:{exc.msg}")
    if not (FACTORY/"engine_runtime.py").is_file():
        findings.append("missing:engine-runtime")
    control=ROOT/"core/control_plane/app.py"
    if not control.is_file():
        findings.append("missing:control-plane")
    else:
        text=control.read_text(encoding="utf-8")
        if "ALLOWED_COMMANDS" not in text:
            findings.append("missing-command-allowlist")
        if "create_subprocess_shell" in text or "shell=True" in text or '"/bin/sh"' in text:
            findings.append("unsafe-shell-executor")
    products=ROOT/"products"/"verticals"
    for name in ("little-oaks","legal","charity"):
        path=products/name
        if not path.is_dir(): findings.append(f"missing-vertical:{name}")
        elif not (path/"A1OS_VERTICAL.json").is_file(): findings.append(f"missing-manifest:{name}")
    result={"status":"PASS" if not findings else "FAIL","engine_count":len(entries),
            "expected":EXPECTED,"findings":findings}
    print(json.dumps(result,indent=2))
    return 0 if not findings else 1

if __name__=="__main__":
    raise SystemExit(main())

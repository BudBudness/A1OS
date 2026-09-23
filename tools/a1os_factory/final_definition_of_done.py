"""System-wide A1OS Product Factory Definition-of-Done audit."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "tools" / "a1os_factory"
ROADMAP = ROOT / "IMPLEMENTATION_ROADMAP.json"
EXPECTED = 37
FORBIDDEN = ("j" + "arvis", "m" + "cp")

def main() -> int:
    findings: list[str] = []
    roadmap = json.loads(ROADMAP.read_text(encoding="utf-8"))
    entries = roadmap.get("roadmap", [])
    if roadmap.get("engines") != EXPECTED or len(entries) != EXPECTED:
        findings.append("engine_count")
    for item in entries:
        path = ROOT / item["engine"]
        if not path.is_file():
            findings.append(f"missing-engine:{item['engine']}")
        if item.get("status") != "IMPLEMENTED":
            findings.append(f"unimplemented:{item['engine']}")
    if not (FACTORY / "engine_runtime.py").is_file():
        findings.append("missing:engine-runtime")
    scan_roots = [ROOT / "core", ROOT / "runtime", ROOT / "tests", FACTORY, ROOT / "products" / "verticals"]
    for base in scan_roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".py", ".html", ".json", ".yml", ".yaml"}:
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
                for token in FORBIDDEN:
                    if token in text:
                        findings.append(f"forbidden:{token}:{path.relative_to(ROOT)}")
                        break
    product_requirements = {
        "little-oaks": ("A1OS_VERTICAL.json",),
        "legal": ("A1OS_VERTICAL.json", "release/RELEASE_STATUS.json", "validation/VALIDATION_REPORT.json"),
        "charity": ("A1OS_VERTICAL.json", "deployments/stramoswisdomcharityorg/PRODUCT.md"),
    }
    for product, candidates in product_requirements.items():
        path = ROOT / "products" / "verticals" / product
        if not path.is_dir():
            findings.append(f"missing-vertical:{product}")
        elif not any((path / candidate).exists() for candidate in candidates):
            findings.append(f"missing-product-evidence:{product}")
    control = (ROOT / "core/control_plane/app.py").read_text(encoding="utf-8", errors="ignore")
    if '"bash"' in control or "bash -lc" in control:
        findings.append("unsafe-shell-executor")
    if "ALLOWED_COMMANDS" not in control:
        findings.append("missing-command-allowlist")
    result = {"status": "PASS" if not findings else "FAIL", "engine_count": len(entries), "expected": EXPECTED, "findings": findings}
    print(json.dumps(result, indent=2))
    return 0 if not findings else 1

if __name__ == "__main__":
    raise SystemExit(main())

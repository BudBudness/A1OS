"""Evidence-based validation for generated A1OS frontend verticals."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("products")
REQUIRED_DIRS = ("pages","components","workflows","forms","integrations","state","assets","tests")

def validate_product(name: str, root: Path = ROOT) -> dict:
    product = root / name
    issues: list[str] = []
    checks = {"exists": product.is_dir(), "manifest": False, "structure": False,
              "manifest_consistent": False, "no_embedded_backend": True,
              "no_embedded_database": True, "python_syntax": True}
    if not product.is_dir():
        issues.append("missing:product")
    else:
        manifest = product / "A1OS_VERTICAL.json"
        checks["manifest"] = manifest.is_file()
        if not manifest.is_file():
            issues.append("missing:A1OS_VERTICAL.json")
        else:
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                checks["manifest_consistent"] = (
                    data.get("name") == name and data.get("type") == "frontend-vertical" and
                    data.get("backend") == "a1os-platform-api" and data.get("customized") is True and
                    isinstance(data.get("requirements"), dict))
            except (OSError, json.JSONDecodeError):
                pass
            if not checks["manifest_consistent"]:
                issues.append("invalid:a1os-manifest")
        checks["structure"] = all((product / item).is_dir() for item in REQUIRED_DIRS)
        if not checks["structure"]:
            issues.append("missing:required-frontend-directories")
        for path in product.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() in {".db",".sqlite",".sqlite3"} or path.name.lower() == "docker-compose.yml":
                checks["no_embedded_database"] = False
                issues.append(f"forbidden:embedded-data:{path.relative_to(product)}")
            if path.name in {"main.py","app.py","server.py"}:
                checks["no_embedded_backend"] = False
                issues.append(f"forbidden:backend-file:{path.relative_to(product)}")
            if path.suffix == ".py":
                try:
                    compile(path.read_text(encoding="utf-8"), str(path), "exec")
                except (OSError, SyntaxError) as exc:
                    checks["python_syntax"] = False
                    issues.append(f"syntax:{path.relative_to(product)}:{exc}")
    status = "healthy" if all(checks.values()) and not issues else "repair_required"
    return {"product": name, "factory_version": "2.1",
            "validation_time": datetime.now(timezone.utc).isoformat(),
            "checks": checks, "issues": issues,
            "repair_plan": [f"repair:{x}" for x in issues], "status": status}

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 validation_engine.py PRODUCT", file=sys.stderr)
        return 2
    report = validate_product(sys.argv[1])
    out = ROOT / sys.argv[1] / "validation"
    out.mkdir(parents=True, exist_ok=True)
    (out / "VALIDATION_REPORT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "healthy" else 1

if __name__ == "__main__":
    raise SystemExit(main())

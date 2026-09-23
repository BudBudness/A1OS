"""Evidence-based validation for generated A1OS products."""
from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("products")

def validate_product(name: str, root: Path = ROOT) -> dict:
    product = root / name
    issues: list[str] = []
    checks = {
        "exists": product.is_dir(),
        "manifest": False,
        "structure": False,
        "no_embedded_backend": True,
        "no_embedded_database": True,
        "python_syntax": True,
    }
    if not product.is_dir():
        issues.append("missing:product")
    else:
        manifests = list(product.glob("A1OS_*.json")) + list(product.glob("**/A1OS_VERTICAL.json"))
        checks["manifest"] = bool(manifests)
        if not manifests:
            issues.append("missing:a1os-manifest")
        required = ["pages", "components", "workflows", "tests"]
        legacy = ["core", "intelligence", "api", "web", "deployments", "docs"]
        checks["structure"] = any((product / item).exists() for item in required) or all((product / item).exists() for item in legacy)
        if not checks["structure"]:
            issues.append("missing:product-structure")
        forbidden = {".db", ".sqlite", ".sqlite3"}
        for path in product.rglob("*"):
            if path.is_file() and (path.suffix.lower() in forbidden or path.name.lower() in {"docker-compose.yml"}):
                checks["no_embedded_database"] = False
                issues.append(f"forbidden:embedded-database:{path.relative_to(product)}")
        backend_markers = {"main.py", "app.py", "server.py"}
        if any(p.is_file() and p.name in backend_markers for p in product.rglob("*")):
            checks["no_embedded_backend"] = False
            issues.append("forbidden:embedded-backend")
        for path in product.rglob("*.py"):
            try:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
            except SyntaxError as exc:
                checks["python_syntax"] = False
                issues.append(f"syntax:{path.relative_to(product)}:{exc.msg}")
    status = "healthy" if all(checks.values()) and not issues else "repair_required"
    return {
        "product": name,
        "factory_version": "2.0",
        "validation_time": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "issues": issues,
        "repair_plan": [f"repair:{issue}" for issue in issues],
        "status": status,
    }

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 validation_engine.py PRODUCT", file=sys.stderr)
        return 2
    name = sys.argv[1]
    report = validate_product(name)
    out = ROOT / name / "validation"
    out.mkdir(parents=True, exist_ok=True)
    (out / "VALIDATION_REPORT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "healthy" else 1

if __name__ == "__main__":
    raise SystemExit(main())

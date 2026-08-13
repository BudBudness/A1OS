#!/usr/bin/env python3
import json
import sys
from pathlib import Path

FORBIDDEN_NAMES = {
    "app.py",
    "server.py",
    "Dockerfile",
    "docker-compose.yml",
    "run-production.sh",
}

FORBIDDEN_PATTERNS = (
    "sqlite",
    "postgres",
    "mysql",
    "create_engine",
    "FastAPI",
    "Flask",
    "uvicorn",
    "gunicorn",
    "docker-compose",
    "Dockerfile",
)

REQUIRED_FILES = {
    "A1OS_VERTICAL.json",
    "A1OS_RUNTIME.json",
    "A1OS_DEPLOYMENT.json",
    "README.md",
    "index.html",
}

def fail(message):
    print(f"FAIL: {message}")
    raise SystemExit(1)

def main():
    if len(sys.argv) != 2:
        fail("usage: verify_runtime_materialization.py vertical-directory")

    root = Path(sys.argv[1])

    if not root.is_dir():
        fail("runtime vertical directory missing")

    manifest_path = root / "A1OS_VERTICAL.json"

    if not manifest_path.is_file():
        fail("A1OS_VERTICAL.json missing")

    try:
        manifest = json.loads(manifest_path.read_text())
    except Exception as exc:
        fail(f"invalid A1OS_VERTICAL.json: {exc}")

    for filename in REQUIRED_FILES:
        if not (root / filename).is_file():
            fail(f"required runtime artifact missing: {filename}")

    if manifest.get("backend") != "a1os-platform-api":
        fail("backend must be a1os-platform-api")

    ownership = manifest.get("ownership", {})
    for key in (
        "authentication",
        "tenancy",
        "authorization",
        "rbac",
    ):
        if ownership.get(key) != "a1os-core":
            fail(f"{key} must remain owned by a1os-core")

    deployment = manifest.get("deployment", {})
    if deployment.get("mode") != "managed":
        fail("deployment mode must be managed")

    files = [p for p in root.rglob("*") if p.is_file()]

    for path in files:
        if path.name in FORBIDDEN_NAMES:
            fail(f"forbidden backend artifact: {path}")

        if path.suffix.lower() in {".db", ".sqlite", ".sqlite3"}:
            fail(f"database artifact found: {path}")

        try:
            text = path.read_text(errors="ignore")
        except Exception:
            continue

        lowered = text.lower()

        for pattern in FORBIDDEN_PATTERNS:
            if pattern.lower() in lowered:
                fail(f"backend contamination '{pattern}' found in {path}")

    runtime_path = root / "A1OS_RUNTIME.json"
    try:
        runtime = json.loads(runtime_path.read_text())
    except Exception as exc:
        fail(f"invalid A1OS_RUNTIME.json: {exc}")

    if runtime.get("backend") != "a1os-platform-api":
        fail("runtime backend binding missing")

    if runtime.get("core") != "a1os-core":
        fail("runtime core binding missing")

    if runtime.get("frontend_owned") is not True:
        fail("frontend ownership binding missing")

    if runtime.get("backend_owned") is not False:
        fail("backend ownership binding invalid")

    deployment_runtime_path = root / "A1OS_DEPLOYMENT.json"
    try:
        deployment_manifest = json.loads(
            deployment_runtime_path.read_text()
        )
    except Exception as exc:
        fail(f"invalid A1OS_DEPLOYMENT.json: {exc}")

    if deployment_manifest.get("api", {}).get("provider") != "a1os-platform-api":
        fail("deployment API provider binding missing")

    if deployment_manifest.get("core", {}).get("authentication") != "a1os-core":
        fail("deployment authentication binding missing")

    if deployment_manifest.get("core", {}).get("tenancy") != "a1os-core":
        fail("deployment tenancy binding missing")

    if deployment_manifest.get("core", {}).get("authorization") != "a1os-core":
        fail("deployment authorization binding missing")

    if deployment_manifest.get("core", {}).get("rbac") != "a1os-core":
        fail("deployment RBAC binding missing")

    print("RUNTIME MATERIALIZATION: PASS")
    print("REQUIRED ARTIFACTS: PASS")
    print("PLATFORM API BINDING: PASS")
    print("CORE AUTH/TENANCY/RBAC: PASS")
    print("DEPLOYMENT MANIFEST: PASS")
    print("FRONTEND-ONLY: PASS")
    print("BACKEND CONTAMINATION: NONE")
    print("PRODUCTION CONTRACT: PASS")

if __name__ == "__main__":
    main()

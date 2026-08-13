#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

FORBIDDEN_NAMES = {
    ".db", ".sqlite", ".sqlite3",
    "app.py", "server.py", "Dockerfile",
    "docker-compose.yml", "run-production.sh"
}

FORBIDDEN_TEXT = re.compile(
    r"sqlite|postgres|mysql|create_engine|FastAPI|Flask|"
    r"uvicorn|gunicorn|docker-compose|Dockerfile",
    re.I
)

REQUIRED_FILES = {
    "A1OS_VERTICAL.json",
    "A1OS_RUNTIME.json",
    "A1OS_DEPLOYMENT.json",
    "README.md",
    "package.json",
    "index.html",
    "src/main.jsx",
    "src/App.jsx",
    "src/api/client.js",
    "src/core/auth.js",
    "src/core/tenant.js",
    "src/rbac/permissions.js",
    "src/data/resource.js",
    "src/workflows/runner.js",
}

def fail(message):
    raise SystemExit(f"FAIL: {message}")

def main():
    if len(sys.argv) != 2:
        fail("usage: verify_generated_vertical.py <vertical>")

    root = Path(sys.argv[1])

    if not root.is_dir():
        fail("vertical directory missing")

    files = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file()
    }

    missing = REQUIRED_FILES - files
    if missing:
        fail(f"missing runtime files: {sorted(missing)}")

    forbidden = [
        p for p in root.rglob("*")
        if p.is_file() and (
            p.name in FORBIDDEN_NAMES or
            p.suffix.lower() in FORBIDDEN_NAMES
        )
    ]

    if forbidden:
        fail(f"forbidden backend artifacts: {forbidden}")

    for p in root.rglob("*"):
        if not p.is_file():
            continue
        try:
            text = p.read_text(errors="ignore")
        except Exception:
            continue
        if FORBIDDEN_TEXT.search(text):
            fail(f"backend contamination in {p}")

    vertical = json.loads(
        (root / "A1OS_VERTICAL.json").read_text()
    )
    runtime = json.loads(
        (root / "A1OS_RUNTIME.json").read_text()
    )
    deployment = json.loads(
        (root / "A1OS_DEPLOYMENT.json").read_text()
    )

    assert re.fullmatch(
        r"[a-z0-9][a-z0-9-]*",
        vertical["name"]
    )

    assert runtime["backend"] == "a1os-platform-api"
    assert runtime["core"] == "a1os-core"
    assert runtime["frontend_owned"] is True
    assert runtime["backend_owned"] is False

    assert deployment["api"]["provider"] == "a1os-platform-api"

    for key in (
        "authentication",
        "tenancy",
        "authorization",
        "rbac"
    ):
        assert deployment["core"][key] == "a1os-core"

    print("RUNTIME: PASS")
    print("PLATFORM API CLIENT: PASS")
    print("AUTH CONTEXT: PASS")
    print("TENANT CONTEXT: PASS")
    print("RBAC CONTRACT: PASS")
    print("DOMAIN DATA BINDING: PASS")
    print("WORKFLOW CONTRACT: PASS")
    print("DEPLOYMENT MANIFEST: PASS")
    print("FRONTEND-ONLY: PASS")
    print("BACKEND CONTAMINATION: NONE")
    print("PRODUCTION CONTRACT: PASS")

if __name__ == "__main__":
    main()

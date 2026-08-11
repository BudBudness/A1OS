#!/usr/bin/env python3

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GENERATOR = (
    ROOT
    / "tools"
    / "a1os_factory"
    / "vertical_os_generator_plane"
    / "vertical_os_generator_engine.py"
)
TEMPLATE = ROOT / "products" / "templates" / "a1os-frontend-template"
VERTICALS = ROOT / "products" / "verticals"


def fail(message):
    print(f"FAIL: {message}")
    raise SystemExit(1)


def normalize(name):
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", name.strip()).strip("-_").lower()
    if not value:
        fail("invalid vertical name")
    return value


def validate_name(name):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
        fail("vertical name must be lowercase kebab-case")


def validate_frontend_only(path):
    forbidden = {
        ".db",
        ".sqlite",
        ".sqlite3",
        ".sql",
        ".py",
    }

    for file in path.rglob("*"):
        if not file.is_file():
            continue
        if file.suffix.lower() in forbidden:
            fail(f"backend artifact detected: {file.relative_to(path)}")

    text = ""
    for file in path.rglob("*"):
        if file.is_file() and file.suffix.lower() in {
            ".json",
            ".md",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".html",
        }:
            try:
                text += file.read_text(errors="ignore") + "\n"
            except OSError:
                pass

    forbidden_refs = [
        "sqlite3",
        "fastapi",
        "flask",
        "uvicorn",
        "DATABASE_PATH",
        "create_engine(",
    ]

    for ref in forbidden_refs:
        if ref.lower() in text.lower():
            fail(f"backend reference detected: {ref}")


def run_generator(name):
    subprocess.run(
        [sys.executable, str(GENERATOR), name],
        cwd=ROOT,
        check=True,
    )


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 frontend_pipeline.py vertical-name")
        raise SystemExit(2)

    requested = sys.argv[1]
    name = normalize(requested)
    validate_name(name)

    output = VERTICALS / name

    if output.exists():
        fail(f"vertical already exists: {output}")

    if not GENERATOR.is_file():
        fail("frontend generator missing")

    if not TEMPLATE.is_dir():
        fail("frontend template missing")

    print("=" * 72)
    print(" A1OS FRONTEND FACTORY — PRODUCTION PIPELINE")
    print("=" * 72)
    print(f"SPECIFICATION: {requested}")
    print(f"VERTICAL:      {name}")
    print(f"BACKEND:       a1os-platform-api")
    print(f"CORE:          a1os-core")
    print(f"OUTPUT:        {output}")

    run_generator(name)

    if not output.is_dir():
        fail("generator did not materialize output")

    contract = output / "A1OS_VERTICAL.json"
    readme = output / "README.md"

    if not contract.is_file():
        fail("A1OS_VERTICAL.json missing")

    if not readme.is_file():
        fail("README.md missing")

    try:
        manifest = json.loads(contract.read_text())
    except json.JSONDecodeError as exc:
        fail(f"invalid vertical contract: {exc}")

    manifest.setdefault("name", name)
    manifest.setdefault("type", "frontend-vertical")
    manifest.setdefault("backend", "a1os-platform-api")
    manifest.setdefault("authentication", "a1os-core")
    manifest.setdefault("tenancy", "a1os-core")
    manifest.setdefault("authorization", "a1os-core")
    manifest.setdefault("rbac", "a1os-core")

    required = {
        "name",
        "type",
        "backend",
        "authentication",
        "tenancy",
        "authorization",
        "rbac",
    }

    missing = sorted(required - manifest.keys())
    if missing:
        fail(f"contract missing fields: {', '.join(missing)}")

    if manifest["type"] != "frontend-vertical":
        fail("invalid vertical type")

    if manifest["backend"] != "a1os-platform-api":
        fail("backend ownership violation")

    for field in ("authentication", "tenancy", "authorization", "rbac"):
        if manifest[field] != "a1os-core":
            fail(f"{field} ownership violation")

    validate_frontend_only(output)

    manifest["pipeline"] = {
        "generator": str(GENERATOR.relative_to(ROOT)),
        "template": str(TEMPLATE.relative_to(ROOT)),
        "backend": "a1os-platform-api",
        "deployment_owner": "vertical",
        "data_owner": "a1os-platform-api",
        "auth_owner": "a1os-core",
        "tenancy_owner": "a1os-core",
        "authorization_owner": "a1os-core",
        "rbac_owner": "a1os-core",
    }

    contract.write_text(json.dumps(manifest, indent=2) + "\n")

    print("\n=== PIPELINE GATE ===")
    print("GENERATION: PASS")
    print("CONTRACT: PASS")
    print("FRONTEND-ONLY: PASS")
    print("BACKEND: A1OS PLATFORM API")
    print("AUTH/TENANCY/RBAC: A1OS CORE")
    print("DATA OWNERSHIP: A1OS PLATFORM API")
    print("DEPLOYMENT OWNERSHIP: VERTICAL")
    print("=" * 72)
    print(f"GENERATED: {output}")
    print("=" * 72)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPEC_SCHEMA = ROOT / "tools/a1os_factory/specifications/vertical_spec.schema.json"
GENERATOR = ROOT / "tools/a1os_factory/vertical_os_generator_plane/vertical_os_generator_engine.py"
OUTPUT_ROOT = ROOT / "products" / "verticals"

FORBIDDEN = {
    ".db", ".sqlite", ".sqlite3", ".sql",
}

FORBIDDEN_NAMES = {
    "database.py",
    "db.py",
    "backend.py",
    "server.py",
    "auth_server.py",
}


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def load_json(path):
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        fail(f"invalid JSON: {path}: {exc}")


def validate_name(name):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
        fail("vertical name must be lowercase kebab-case")


def validate_spec(spec):
    required = {
        "name",
        "display_name",
        "description",
        "domain",
        "pages",
        "features",
        "deployment",
    }

    missing = required - set(spec)
    if missing:
        fail(f"missing specification fields: {sorted(missing)}")

    validate_name(spec["name"])

    if not isinstance(spec["pages"], list):
        fail("pages must be a list")

    if not isinstance(spec["features"], list):
        fail("features must be a list")

    backend = spec.get("backend", {})
    if backend and backend.get("provider") != "a1os-platform-api":
        fail("backend ownership must remain a1os-platform-api")

    ownership = spec.get("ownership", {})
    for key in (
        "authentication",
        "tenancy",
        "authorization",
        "rbac",
    ):
        if ownership and ownership.get(key) != "a1os-core":
            fail(f"{key} must remain a1os-core")


def validate_output(root):
    if not root.is_dir():
        fail(f"generator did not create output: {root}")

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() in FORBIDDEN:
            fail(f"backend/database artifact generated: {path}")

        if path.name.lower() in FORBIDDEN_NAMES:
            fail(f"backend artifact generated: {path}")


def main():
    if len(sys.argv) != 2:
        fail("usage: build_from_spec.py path/to/spec.json")

    spec_path = Path(sys.argv[1]).resolve()

    if not spec_path.is_file():
        fail(f"specification not found: {spec_path}")

    schema = load_json(SPEC_SCHEMA)
    spec = load_json(spec_path)

    validate_spec(spec)

    name = spec["name"]
    output = OUTPUT_ROOT / name

    if output.exists():
        fail(f"refusing to overwrite existing vertical: {output}")

    subprocess.run(
        [sys.executable, str(GENERATOR), name],
        cwd=ROOT,
        check=True,
    )

    validate_output(output)

    manifest = {
        "type": "frontend-vertical",
        "name": name,
        "display_name": spec["display_name"],
        "domain": spec["domain"],
        "backend": "a1os-platform-api",
        "authentication": "a1os-core",
        "tenancy": "a1os-core",
        "authorization": "a1os-core",
        "rbac": "a1os-core",
        "specification": str(spec_path.relative_to(ROOT)),
    }

    (output / "A1OS_BUILD.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )

    validate_output(output)

    print(f"A1OS Frontend Built: {output}")
    print("SPECIFICATION: PASS")
    print("GENERATION: PASS")
    print("FRONTEND-ONLY: PASS")
    print("BACKEND: A1OS PLATFORM API")
    print("AUTH/TENANCY/RBAC: A1OS CORE")


if __name__ == "__main__":
    main()

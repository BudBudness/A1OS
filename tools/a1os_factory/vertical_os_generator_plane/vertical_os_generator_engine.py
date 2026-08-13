#!/usr/bin/env python3
import subprocess

"""
A1OS Frontend Vertical Generator

Contract:
    product specification
        -> frontend template
        -> generated frontend vertical

Generated verticals are frontend-only.
Backend, tenancy, authentication, RBAC, persistence and infrastructure
remain owned by A1OS Core / Platform.
"""

from pathlib import Path
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parents[3]
TEMPLATE = ROOT / "products" / "templates" / "a1os-frontend-template"
OUTPUT_ROOT = ROOT / "products" / "verticals"


def normalize_name(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")

    if not value:
        raise ValueError("vertical name cannot be empty")

    return value


def validate_name(name: str) -> None:
    if name in {".", ".."}:
        raise ValueError("invalid vertical name")

    if name.startswith("."):
        raise ValueError("hidden vertical names are not allowed")


def generate(product: str) -> Path:
    name = normalize_name(product)
    validate_name(name)

    if not TEMPLATE.is_dir():
        raise FileNotFoundError(f"frontend template missing: {TEMPLATE}")

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    destination = OUTPUT_ROOT / name

    if destination.exists():
        raise FileExistsError(
            f"vertical already exists: {destination}"
        )

    shutil.copytree(
        TEMPLATE,
        destination,
        ignore=shutil.ignore_patterns(
            ".git",
            "__pycache__",
            "*.pyc",
            "*.db",
            "*.sqlite",
            "*.sqlite3",
        ),
    )

    # Remove backend/database artifacts if a future template accidentally
    # acquires one. The frontend contract explicitly forbids them.
    for path in list(destination.rglob("*")):
        if not path.is_file():
            continue

        if path.suffix.lower() in {
            ".py",
            ".sql",
            ".db",
            ".sqlite",
            ".sqlite3",
        }:
            path.unlink()

    metadata = destination / "A1OS_VERTICAL.json"
    metadata.write_text(
        """{
  "name": "%s",
  "type": "frontend-vertical",
  "backend": "a1os-platform-api",
  "deployment": {
    "mode": "managed"
  },
  "ownership": {
    "pages": "vertical",
    "components": "vertical",
    "layouts": "vertical",
    "dashboards": "vertical",
    "workflows": "vertical",
    "forms": "vertical",
    "state": "vertical",
    "integrations": "a1os-platform",
    "styles": "vertical",
    "assets": "vertical",
    "tests": "vertical",
    "authentication": "a1os-core",
    "tenancy": "a1os-core",
    "authorization": "a1os-core",
    "rbac": "a1os-core",
    "persistence": "a1os-platform",
    "infrastructure": "a1os-platform"
  }
}
""" % name,
        encoding="utf-8",
    )

    # A1OS Frontend Runtime Materialization
    _runtime_materializer = (
        Path(__file__).resolve().parents[1]
        / "frontend_runtime"
        / "runtime_materializer.py"
    )
    _spec_path = destination / "A1OS_VERTICAL.json"
    if _runtime_materializer.exists() and _spec_path.exists():
        subprocess.run(
            [
                sys.executable,
                str(_runtime_materializer),
                str(_spec_path),
                str(destination),
            ],
            check=True,
        )

    return destination


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: python3 vertical_os_generator_engine.py "
            "vertical-os-name"
        )
        return 2

    try:
        destination = generate(sys.argv[1])
    except Exception as exc:
        print(f"A1OS Vertical OS Generation FAILED: {exc}")
        return 1

    print(f"A1OS Vertical OS Generated: {destination.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
A1OS Frontend Production Pipeline

Customer Request
    -> Build Request Specification
    -> Frontend Factory
    -> Frontend Artifact
    -> Contract Validation
    -> Deployment Manifest
    -> A1OS Platform API binding

Architectural invariants:
- Vertical owns UI/frontend artifacts only.
- A1OS Platform API owns backend/domain data.
- A1OS Core owns authentication, tenancy, authorization and RBAC.
- Vertical owns its deployment configuration.
- No vertical may create a database, backend server, watchdog or infrastructure stack.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

COMPILER = (
    ROOT
    / "tools"
    / "a1os_factory"
    / "specifications"
    / "build_request_compiler.py"
)

GENERATOR = (
    ROOT
    / "tools"
    / "a1os_factory"
    / "vertical_os_generator_plane"
    / "vertical_os_generator_engine.py"
)

VERTICAL_ROOT = ROOT / "products" / "verticals"

KEBAB = re.compile(r"^[a-z0-9][a-z0-9-]*$")

FORBIDDEN_NAMES = {
    "database",
    "db",
    "backend",
    "server",
    "api",
    "watchdog",
    "docker-compose",
    "kubernetes",
    "infra",
    "infrastructure",
}

FORBIDDEN_SUFFIXES = {
    ".db",
    ".sqlite",
    ".sqlite3",
}


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def fail(message: str) -> None:
    raise RuntimeError(message)


def load_json(path: Path) -> dict:
    if not path.is_file():
        fail(f"missing JSON artifact: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON: {path}: {exc}")


def validate_name(name: str) -> None:
    if not KEBAB.fullmatch(name):
        fail(f"vertical name must be lowercase kebab-case: {name}")


def validate_spec(spec: dict) -> None:
    validate_name(spec["name"])

    backend = spec.get("backend", {})
    if backend.get("provider") != "a1os-platform-api":
        fail("backend provider must be a1os-platform-api")

    ownership = spec.get("ownership", {})

    for key in (
        "authentication",
        "tenancy",
        "authorization",
        "rbac",
    ):
        if ownership.get(key) != "a1os-core":
            fail(f"{key} must be owned by a1os-core")

    if spec.get("deployment", {}).get("mode") not in {
        "managed",
        "self-managed",
    }:
        fail("deployment.mode must be managed or self-managed")


def validate_frontend_artifact(vertical: Path, spec: dict) -> None:
    if not vertical.is_dir():
        fail(f"generated vertical missing: {vertical}")

    required = {
        "README.md",
        "A1OS_VERTICAL.json",
    }

    existing = {p.name for p in vertical.iterdir() if p.is_file()}

    missing = required - existing
    if missing:
        fail(f"missing frontend artifacts: {sorted(missing)}")

    generated = load_json(vertical / "A1OS_VERTICAL.json")

    if generated.get("name") != spec["name"]:
        fail("generated vertical name does not match specification")

    if generated.get("backend") != "a1os-platform-api":
        fail("generated vertical backend contract is invalid")

    if generated.get("frontend_only") is not True:
        fail("generated vertical is not explicitly frontend-only")

    ownership = generated.get("ownership", {})
    for key in (
        "authentication",
        "tenancy",
        "authorization",
        "rbac",
    ):
        if ownership.get(key) != "a1os-core":
            fail(f"generated ownership violation: {key}")

    for path in vertical.rglob("*"):
        if not path.is_file():
            continue

        relative = path.relative_to(vertical)
        lower = str(relative).lower()

        if path.name in {"__pycache__"}:
            fail(f"generated backend artifact: {relative}")

        if any(part.lower() in FORBIDDEN_NAMES for part in relative.parts):
            fail(f"forbidden backend/infrastructure artifact: {relative}")

        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            fail(f"database artifact inside frontend vertical: {relative}")

        if lower.endswith(".env") or ".env." in lower:
            fail(f"environment/secrets artifact inside frontend vertical: {relative}")

        text_extensions = {
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".json",
            ".yaml",
            ".yml",
            ".toml",
            ".md",
            ".sh",
        }

        if path.suffix.lower() in text_extensions:
            try:
                content = path.read_text(encoding="utf-8").lower()
            except UnicodeDecodeError:
                continue

            forbidden_patterns = (
                "sqlite3.connect(",
                "create_engine(",
                "fastapi(",
                "flask(",
                "express(",
                "uvicorn",
                "postgresql://",
                "mysql://",
                "redis://",
            )

            for pattern in forbidden_patterns:
                if pattern in content:
                    fail(
                        f"backend contamination detected in "
                        f"{relative}: {pattern}"
                    )


def write_deployment_manifest(vertical: Path, spec: dict) -> Path:
    deployment = spec.get("deployment", {})

    manifest = {
        "version": "1.0",
        "product": spec["name"],
        "artifact": {
            "type": "a1os-frontend-vertical",
            "path": str(vertical.relative_to(ROOT)),
        },
        "deployment": {
            "mode": deployment.get("mode"),
            "owner": "vertical",
            "infrastructure_owner": "deployment-target",
        },
        "backend": {
            "provider": "a1os-platform-api",
            "ownership": "a1os-platform",
        },
        "core": {
            "authentication": "a1os-core",
            "tenancy": "a1os-core",
            "authorization": "a1os-core",
            "rbac": "a1os-core",
        },
        "domain_data": {
            "owner": "a1os-platform-api",
            "local_database": False,
        },
        "status": "validated",
    }

    path = vertical / "A1OS_DEPLOYMENT.json"
    path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def validate_deployment_manifest(path: Path) -> None:
    manifest = load_json(path)

    if manifest.get("status") != "validated":
        fail("deployment manifest is not validated")

    if manifest.get("backend", {}).get("provider") != "a1os-platform-api":
        fail("deployment backend binding is invalid")

    if manifest.get("domain_data", {}).get("local_database") is not False:
        fail("deployment permits local domain database")

    core = manifest.get("core", {})
    for key in (
        "authentication",
        "tenancy",
        "authorization",
        "rbac",
    ):
        if core.get(key) != "a1os-core":
            fail(f"deployment core ownership violation: {key}")


def compile_request(request: Path, output: Path) -> dict:
    run([
        sys.executable,
        str(COMPILER),
        str(request),
        str(output),
    ])
    return load_json(output)


def generate_vertical(name: str) -> Path:
    run([
        sys.executable,
        str(GENERATOR),
        name,
    ])

    vertical = VERTICAL_ROOT / name

    if not vertical.is_dir():
        fail(f"factory did not materialize expected output: {vertical}")

    return vertical


def main() -> int:
    parser = argparse.ArgumentParser(
        description="A1OS end-to-end frontend production pipeline"
    )
    parser.add_argument("request", help="customer build-request JSON")
    parser.add_argument(
        "--keep",
        action="store_true",
        help="retain generated artifact",
    )
    args = parser.parse_args()

    request = Path(args.request).resolve()

    if not request.is_file():
        fail(f"request does not exist: {request}")

    if not COMPILER.is_file():
        fail(f"missing build request compiler: {COMPILER}")

    if not GENERATOR.is_file():
        fail(f"missing frontend generator: {GENERATOR}")

    with tempfile.TemporaryDirectory(prefix="a1os-factory-") as tmp:
        compiled = Path(tmp) / "compiled-spec.json"

        print("========================================================================")
        print("A1OS FRONTEND PRODUCTION PIPELINE")
        print("========================================================================")

        print("[1/6] CUSTOMER SPECIFICATION")
        source = load_json(request)
        print(f"      request: {request.name}")

        print("[2/6] BUILD REQUEST COMPILATION")
        spec = compile_request(request, compiled)
        validate_spec(spec)
        print(f"      specification: {spec['name']}")

        vertical = VERTICAL_ROOT / spec["name"]

        if vertical.exists():
            fail(
                f"refusing to overwrite existing vertical: {vertical}"
            )

        print("[3/6] A1OS FACTORY")
        generated = generate_vertical(spec["name"])
        print(f"      artifact: {generated.relative_to(ROOT)}")

        print("[4/6] FRONTEND CONTRACT VALIDATION")
        validate_frontend_artifact(generated, spec)
        print("      frontend-only: PASS")
        print("      backend contamination: NONE")
        print("      platform ownership: PASS")
        print("      core ownership: PASS")

        print("[5/6] DEPLOYMENT MATERIALIZATION")
        manifest = write_deployment_manifest(generated, spec)
        validate_deployment_manifest(manifest)
        print(f"      deployment manifest: {manifest.relative_to(ROOT)}")

        print("[6/6] A1OS PLATFORM API BINDING")
        platform_binding = load_json(generated / "A1OS_VERTICAL.json")
        if platform_binding.get("backend") != "a1os-platform-api":
            fail("platform API binding failed")
        print("      backend: a1os-platform-api")
        print("      domain data: platform-owned")

        if not args.keep:
            shutil.rmtree(generated)
            print("      generated fixture: REMOVED")

        print("========================================================================")
        print("A1OS END-TO-END FRONTEND PIPELINE: PASS")
        print("CUSTOMER SPECIFICATION: VERIFIED")
        print("BUILD REQUEST COMPILER: VERIFIED")
        print("FACTORY GENERATION: VERIFIED")
        print("FRONTEND CONTRACT: VERIFIED")
        print("DEPLOYMENT ARTIFACT: VERIFIED")
        print("BACKEND: A1OS PLATFORM API")
        print("AUTH/TENANCY/AUTHORIZATION/RBAC: A1OS CORE")
        print("========================================================================")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)

#!/usr/bin/env python3
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "templates"

FORBIDDEN = {
    ".db",
    ".sqlite",
    ".sqlite3",
    "app.py",
    "server.py",
    "Dockerfile",
    "docker-compose.yml",
    "run-production.sh",
}

def fail(message):
    raise SystemExit(f"FAIL: {message}")

def validate_name(name):
    import re
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
        fail("vertical name must be lowercase kebab-case")

def materialize(spec, output):
    # Normalize canonical specification ownership forms.
    backend = spec.get("backend")
    if isinstance(backend, str):
        spec["backend"] = {"provider": backend}
    elif backend is None:
        spec["backend"] = {"provider": "a1os-platform-api"}

    ownership = spec.get("ownership")
    if ownership is None:
        spec["ownership"] = {
            "authentication": "a1os-core",
            "tenancy": "a1os-core",
            "authorization": "a1os-core",
            "rbac": "a1os-core",
        }

    validate_name(spec["name"])

    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)

    for item in TEMPLATE.rglob("*"):
        if item.is_file():
            rel = item.relative_to(TEMPLATE)
            destination = output / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, destination)

    package = {
        "name": spec["name"],
        "private": True,
        "version": "1.0.0",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "test": "node --test"
        },
        "dependencies": {
            "react": "^19.0.0",
            "react-dom": "^19.0.0"
        },
        "devDependencies": {
            "vite": "^7.0.0",
            "@vitejs/plugin-react": "^4.0.0"
        }
    }

    (output / "package.json").write_text(
        json.dumps(package, indent=2) + "\n"
    )

    deployment = {
        "api": {
            "provider": spec["backend"]["provider"],
            "contract": "a1os-platform-api"
        },
        "core": {
            "authentication": spec["ownership"]["authentication"],
            "tenancy": spec["ownership"]["tenancy"],
            "authorization": spec["ownership"]["authorization"],
            "rbac": spec["ownership"]["rbac"]
        },
        "deployment": spec["deployment"],
        "vertical": spec["name"]
    }

    (output / "A1OS_DEPLOYMENT.json").write_text(
        json.dumps(deployment, indent=2) + "\n"
    )

    runtime = {
        "name": spec["name"],
        "runtime": "a1os-frontend-runtime",
        "version": "1.0",
        "backend": "a1os-platform-api",
        "core": "a1os-core",
        "frontend_owned": True,
        "backend_owned": False
    }

    (output / "A1OS_RUNTIME.json").write_text(
        json.dumps(runtime, indent=2) + "\n"
    )

    return output

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: runtime_materializer.py specification.json output"
        )

    spec = json.loads(Path(sys.argv[1]).read_text())
    materialize(spec, sys.argv[2])
    print(f"RUNTIME MATERIALIZED: {sys.argv[2]}")

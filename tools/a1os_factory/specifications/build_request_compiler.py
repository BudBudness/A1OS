#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "tools/a1os_factory/specifications/vertical_spec.schema.json"


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def kebab(value):
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    if not value:
        fail("unable to derive vertical name")
    return value


def compile_request(request):
    if not isinstance(request, dict):
        fail("build request must be an object")

    required = {
        "name",
        "description",
        "domain",
        "pages",
        "features",
    }

    missing = required - set(request)
    if missing:
        fail(f"missing build request fields: {sorted(missing)}")

    name = kebab(request["name"])

    if not isinstance(request["pages"], list):
        fail("pages must be a list")

    if not isinstance(request["features"], list):
        fail("features must be a list")

    pages = []

    for page in request["pages"]:
        if isinstance(page, str):
            page_name = page.strip()
            route = "/" + kebab(page_name)
            if page_name.lower() in {"dashboard", "home"}:
                route = "/"
        elif isinstance(page, dict):
            page_name = str(page.get("name", "")).strip()
            route = str(page.get("route", "")).strip()
            if not page_name or not route:
                fail("page objects require name and route")
        else:
            fail("pages must contain strings or objects")

        pages.append({
            "name": page_name,
            "route": route
        })

    features = [
        str(feature).strip()
        for feature in request["features"]
        if str(feature).strip()
    ]

    spec = {
        "name": name,
        "display_name": request.get(
            "display_name",
            f"{request['name'].strip()} OS"
        ),
        "description": str(request["description"]).strip(),
        "domain": str(request["domain"]).strip(),
        "pages": pages,
        "features": features,
        "deployment": {
            "mode": request.get("deployment", "managed")
        },
        "backend": {
            "provider": "a1os-platform-api"
        },
        "ownership": {
            "authentication": "a1os-core",
            "tenancy": "a1os-core",
            "authorization": "a1os-core",
            "rbac": "a1os-core"
        }
    }

    return spec


def validate_spec(spec):
    schema = json.loads(SCHEMA.read_text())

    assert schema["title"] == "A1OS Frontend Vertical Specification"
    assert re.fullmatch(r"[a-z0-9][a-z0-9-]*", spec["name"])
    assert spec["backend"]["provider"] == "a1os-platform-api"

    for key in (
        "authentication",
        "tenancy",
        "authorization",
        "rbac"
    ):
        assert spec["ownership"][key] == "a1os-core"

    assert isinstance(spec["pages"], list)
    assert isinstance(spec["features"], list)


def main():
    if len(sys.argv) != 3:
        fail(
            "usage: build_request_compiler.py "
            "request.json output-spec.json"
        )

    request_path = Path(sys.argv[1]).resolve()
    output_path = Path(sys.argv[2]).resolve()

    if not request_path.is_file():
        fail(f"request not found: {request_path}")

    request = json.loads(request_path.read_text())
    spec = compile_request(request)
    validate_spec(spec)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(spec, indent=2) + "\n")

    print(f"A1OS Vertical Specification: {output_path}")
    print("REQUEST: PASS")
    print("COMPILATION: PASS")
    print("SPECIFICATION: PASS")
    print("BACKEND: A1OS PLATFORM API")
    print("AUTH/TENANCY/RBAC: A1OS CORE")


if __name__ == "__main__":
    main()

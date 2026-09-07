#!/usr/bin/env python3
"""
A1OS One-Click Product Factory

Build:
    python3 one_click_factory.py <template-slug> <product>

Build + deployment:
    python3 one_click_factory.py --deploy <template-slug> <product>

The factory delegates generation to the canonical vertical generator.
Deployment is delegated to the existing A1OS deployment authority.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATOR = (
    ROOT
    / "tools"
    / "a1os_factory"
    / "vertical_os_generator_plane"
    / "vertical_os_generator_engine.py"
)

CATALOG = (
    ROOT
    / "products"
    / "templates"
    / "vertical-catalog"
    / "catalog.json"
)

DEPLOYMENT_PLANE = (
    ROOT
    / "tools"
    / "a1os_factory"
    / "deployment_plane"
    / "deployment_plane.py"
)

VERTICAL_ROOT = ROOT / "products" / "verticals"


def fail(message):
    print(f"A1OS ONE-CLICK FACTORY FAILED: {message}")
    raise SystemExit(1)


def load_templates():
    if not CATALOG.exists():
        fail(f"catalog not found: {CATALOG}")

    data = json.loads(CATALOG.read_text())

    if isinstance(data, dict):
        templates = data.get("templates", [])
    elif isinstance(data, list):
        templates = data
    else:
        fail("invalid vertical catalog format")

    result = []

    for item in templates:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict):
            slug = item.get("slug") or item.get("name")
            if slug:
                result.append(slug)

    return sorted(set(result))


def validate_template(template_slug):
    templates = load_templates()

    if template_slug not in templates:
        fail(
            f"unknown template '{template_slug}'. "
            f"Available templates: {', '.join(templates)}"
        )


def validate_product(product):
    if not product:
        fail("product name is required")

    if "/" in product or "\\" in product or ".." in product:
        fail("invalid product name")

    if product.startswith("."):
        fail("invalid product name")


def generate(template_slug, product):
    # The canonical generator normalizes product names before creating
    # the filesystem destination. Do not assume the raw CLI name is the
    # directory name.
    normalized = product.strip().lower().replace("_", "-").replace(" ", "-")
    destination = VERTICAL_ROOT / normalized

    if destination.exists():
        fail(f"vertical already exists: {destination}")

    print("============================================================")
    print("A1OS // ONE-CLICK GENERATION")
    print("============================================================")
    print(f"TEMPLATE={template_slug}")
    print(f"PRODUCT={product}")
    print("GENERATION=START")

    subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            template_slug,
            product,
        ],
        cwd=ROOT,
        check=True,
    )

    if not destination.exists():
        candidates = sorted(
            (
                path for path in VERTICAL_ROOT.iterdir()
                if path.is_dir()
                and (
                    (path / "A1OS_VERTICAL.json").exists()
                    or (path / "A1OS_RUNTIME.json").exists()
                    or (path / "A1OS_DEPLOYMENT.json").exists()
                )
            ),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        if candidates:
            destination = candidates[0]
        else:
            fail("generator completed without creating the vertical")
    print("GENERATION=PASS")
    print(f"VERTICAL={destination.relative_to(ROOT)}")

    return destination


def verify_vertical(destination):
    required = (
        "A1OS_VERTICAL.json",
        "A1OS_RUNTIME.json",
        "A1OS_DEPLOYMENT.json",
    )

    missing = [
        name for name in required
        if not (destination / name).exists()
    ]

    if missing:
        fail(f"generated vertical missing manifests: {', '.join(missing)}")

    deployment = json.loads(
        (destination / "A1OS_DEPLOYMENT.json").read_text()
    )

    if deployment.get("api", {}).get("provider") != "a1os-platform-api":
        fail("invalid platform API binding")

    core = deployment.get("core", {})

    for key in (
        "authentication",
        "tenancy",
        "authorization",
        "rbac",
    ):
        if core.get(key) != "a1os-core":
            fail(f"invalid A1OS core binding: {key}")

    if deployment.get("deployment", {}).get("mode") != "managed":
        fail("managed deployment contract missing")

    print("VERTICAL_CONTRACT=PASS")


def deploy(product):
    if not DEPLOYMENT_PLANE.exists():
        fail(
            "deployment authority not found: "
            f"{DEPLOYMENT_PLANE.relative_to(ROOT)}"
        )

    print("============================================================")
    print("A1OS // ONE-CLICK DEPLOYMENT")
    print("============================================================")
    print(f"PRODUCT={product}")
    print("DEPLOYMENT=START")

    subprocess.run(
        [
            sys.executable,
            str(DEPLOYMENT_PLANE),
            product,
        ],
        cwd=ROOT,
        check=True,
    )

    print("DEPLOYMENT=PASS")


def main():
    parser = argparse.ArgumentParser(
        description="A1OS one-click product factory"
    )

    parser.add_argument(
        "template_slug",
        help="catalog template slug",
    )

    parser.add_argument(
        "product",
        help="vertical/product name",
    )

    parser.add_argument(
        "--deploy",
        action="store_true",
        help="run the deployment stage after generation",
    )

    args = parser.parse_args()

    validate_template(args.template_slug)
    validate_product(args.product)

    destination = generate(
        args.template_slug,
        args.product,
    )

    verify_vertical(destination)

    if args.deploy:
        deploy(args.product)
    else:
        print("DEPLOYMENT=SKIPPED")
        print("DEPLOYMENT_MODE=BUILD_ONLY")

    print("============================================================")
    print("A1OS // ONE-CLICK FACTORY")
    print("============================================================")
    print("BUILD=PASS")
    print(f"PRODUCT={args.product}")
    print(f"TEMPLATE={args.template_slug}")
    print(f"VERTICAL={destination.relative_to(ROOT)}")
    print(f"DEPLOYMENT={'PASS' if args.deploy else 'SKIPPED'}")
    print("PRODUCTION_EXECUTION=YES" if args.deploy else "PRODUCTION_EXECUTION=NO")
    print("SECRETS_DISPLAYED=NO")
    print("============================================================")


if __name__ == "__main__":
    main()

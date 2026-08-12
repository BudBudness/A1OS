from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import WorkflowEngine
from .registry import Registry


def main() -> int:
    parser = argparse.ArgumentParser(prog="a1os-engineering")
    parser.add_argument("command", choices=["list-capabilities", "list-workflows", "plan", "run"])
    parser.add_argument("identifier", nargs="?")
    parser.add_argument("--registry", default="engineering/registry")
    parser.add_argument("--runs", default="engineering/runs")
    parser.add_argument("--execute", action="store_true", help="request execution instead of the default dry-run")
    args = parser.parse_args()

    registry = Registry(args.registry)
    registry.discover()

    if args.command == "list-capabilities":
        print(json.dumps(sorted(registry.capabilities), indent=2))
        return 0
    if args.command == "list-workflows":
        print(json.dumps(sorted(registry.workflows), indent=2))
        return 0
    if not args.identifier:
        parser.error("identifier is required")

    engine = WorkflowEngine(registry, args.runs)
    if args.command == "plan":
        print(json.dumps(engine.plan(args.identifier), indent=2))
    else:
        print(json.dumps(engine.start(args.identifier, dry_run=not args.execute), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

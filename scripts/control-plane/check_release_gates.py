#!/usr/bin/env python3
"""Fail-closed release gate evaluator for the canonical control plane."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

REQUIRED = {
    "canonical_instructions_on_main",
    "global_repository_reconciliation",
    "working_copy_drift_check",
    "automated_instruction_integrity",
    "agent_preflight",
    "security_and_provider_boundary",
    "engineering_workflow",
    "isolated_staging",
    "backup_restore_and_rollback",
    "independent_runtime_verification",
    "release_approval",
}
ACCEPTED = {"verified", "ci_verified"}

def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("unsupported release gate schema_version")
    ids = [gate.get("id") for gate in data.get("gates", [])]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate release gate id")
    missing = REQUIRED - set(ids)
    if missing:
        raise ValueError("missing required gates: " + ", ".join(sorted(missing)))
    if data.get("platform") != ["GitHub", "Cloudflare", "Termux"]:
        raise ValueError("canonical platform must remain GitHub + Cloudflare + Termux")
    return data

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("canonical-control-plane/config/release-gates.json"))
    parser.add_argument("--evaluate", action="store_true")
    args = parser.parse_args()
    try:
        data = load(args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"RELEASE GATE CONFIGURATION: FAIL: {exc}")
        return 1
    print(f"Release status: {data.get('release_status')}")
    print(f"Production deployment enabled: {data.get('production_deployment_enabled')}")
    if not args.evaluate:
        print(f"Release gate manifest: VALID ({len(data['gates'])} gates)")
        return 0
    gaps = [g for g in data["gates"] if g.get("status") not in ACCEPTED or not g.get("evidence")]
    if gaps or data.get("release_status") != "READY" or data.get("production_deployment_enabled") is not True:
        for gate in gaps:
            print(f"BLOCKED: {gate['id']} status={gate.get('status')} evidence={gate.get('evidence')}")
        print("PRODUCTION RELEASE: BLOCKED")
        return 2
    print("PRODUCTION RELEASE: READY")
    return 0

if __name__ == "__main__":
    sys.exit(main())

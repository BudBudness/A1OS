import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.getcwd())

from core.state import A1OS


async def main():
    app = A1OS()
    cases = []

    tests = sorted(
        Path(".").glob("*integrity_test.py")
    )

    for test in tests:
        compile_result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(test)],
            capture_output=True,
            text=True,
        )
        run_result = subprocess.run(
            [sys.executable, str(test)],
            capture_output=True,
            text=True,
        )

        cases.append({
            "name": test.name,
            "passed": (
                compile_result.returncode == 0
                and run_result.returncode == 0
            ),
        })

    capability = "digital_world_recovery"
    entity_id = "primary-device"
    action = "repair"

    result = await app._universal_consequence_gate(
        capability=capability,
        kwargs={
            "entity_id": entity_id,
            "target_action": action,
        },
    )

    provenance = result.get("provenance", {})

    cases.extend([
        {
            "name": "live_control_plane_authorization",
            "passed": result.get("allowed") is True,
        },
        {
            "name": "live_provenance_verification",
            "passed": app._verify_authorization_provenance(
                provenance
            ),
        },
        {
            "name": "live_context_binding",
            "passed": (
                provenance.get("capability") == capability
                and provenance.get("entity_id") == entity_id
                and provenance.get("action") == action
            ),
        },
    ])

    failed = [
        case
        for case in cases
        if not case["passed"]
    ]

    output = {
        "status": (
            "control_plane_regression_baseline_passed"
            if not failed
            else "control_plane_regression_baseline_failed"
        ),
        "total": len(cases),
        "passed": len(cases) - len(failed),
        "failed": len(failed),
        "tests": cases,
    }

    print(json.dumps(output, indent=2))

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())

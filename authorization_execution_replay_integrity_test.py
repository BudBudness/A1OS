import asyncio
import copy
import json
import os
import sys

sys.path.insert(0, os.getcwd())

from core.state import A1OS


async def main():
    app = A1OS()

    capability = "digital_world_recovery"
    entity_id = "primary-device"
    action = "repair"

    first = await app._universal_consequence_gate(
        capability=capability,
        kwargs={
            "entity_id": entity_id,
            "target_action": action,
        },
    )

    second = await app._universal_consequence_gate(
        capability=capability,
        kwargs={
            "entity_id": entity_id,
            "target_action": action,
        },
    )

    first_auth = first.get("authorization", {})
    second_auth = second.get("authorization", {})
    first_provenance = first.get("provenance", {})
    second_provenance = second.get("provenance", {})

    cases = []

    cases.append({
        "name": "first_execution_authorization_is_valid",
        "passed": (
            first.get("allowed") is True
            and app._verify_authorization_provenance(
                first_provenance
            )
        ),
    })

    cases.append({
        "name": "second_execution_authorization_is_valid",
        "passed": (
            second.get("allowed") is True
            and app._verify_authorization_provenance(
                second_provenance
            )
        ),
    })

    cases.append({
        "name": "authorization_decisions_are_not_reused",
        "passed": (
            first_auth.get("provenance", {}).get(
                "authorization_id"
            )
            != second_auth.get("provenance", {}).get(
                "authorization_id"
            )
        ),
    })

    cases.append({
        "name": "execution_provenance_records_are_unique",
        "passed": (
            first_provenance.get("provenance_id")
            != second_provenance.get("provenance_id")
        ),
    })

    cases.append({
        "name": "execution_timestamps_are_reissued",
        "passed": (
            first_provenance.get("timestamp")
            != second_provenance.get("timestamp")
        ),
    })

    replayed_kwargs = {
        "entity_id": entity_id,
        "target_action": action,
        "authorization": copy.deepcopy(first_auth),
        "provenance": copy.deepcopy(first_provenance),
    }

    replayed = await app._universal_consequence_gate(
        capability=capability,
        kwargs=replayed_kwargs,
    )

    replayed_provenance = replayed.get(
        "provenance",
        {},
    )

    cases.append({
        "name": "replayed_authorization_cannot_replace_fresh_decision",
        "passed": (
            replayed_provenance.get("provenance_id")
            != first_provenance.get("provenance_id")
            and replayed_provenance.get("record_hash")
            != first_provenance.get("record_hash")
        ),
    })

    forged_replay = copy.deepcopy(first_provenance)
    forged_replay["timestamp"] = 0

    cases.append({
        "name": "stale_provenance_replay_fails_integrity",
        "passed": not app._verify_authorization_provenance(
            forged_replay
        ),
    })

    failed = [
        case
        for case in cases
        if not case["passed"]
    ]

    result = {
        "status": (
            "authorization_execution_replay_integrity_test_passed"
            if not failed
            else "authorization_execution_replay_integrity_test_failed"
        ),
        "total": len(cases),
        "passed": len(cases) - len(failed),
        "failed": len(failed),
        "tests": cases,
    }

    print(json.dumps(result, indent=2))

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())

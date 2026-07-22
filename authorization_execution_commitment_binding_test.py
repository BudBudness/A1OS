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

    result = await app._universal_consequence_gate(
        capability=capability,
        kwargs={
            "entity_id": entity_id,
            "target_action": action,
        },
    )

    authorization = result.get("authorization", {})
    provenance = result.get("provenance", {})

    cases = []

    cases.append({
        "name": "commitment_capability_binding_is_exact",
        "passed": (
            result.get("capability") == capability
            and provenance.get("capability") == capability
        ),
    })

    cases.append({
        "name": "commitment_entity_binding_is_exact",
        "passed": (
            provenance.get("entity_id") == entity_id
        ),
    })

    cases.append({
        "name": "commitment_action_binding_is_exact",
        "passed": (
            provenance.get("action") == action
        ),
    })

    tampered = copy.deepcopy(provenance)
    tampered["capability"] = "filesystem_management"

    cases.append({
        "name": "capability_rebinding_invalidates_commitment",
        "passed": not app._verify_authorization_provenance(tampered),
    })

    tampered = copy.deepcopy(provenance)
    tampered["entity_id"] = "attacker"

    cases.append({
        "name": "entity_rebinding_invalidates_commitment",
        "passed": not app._verify_authorization_provenance(tampered),
    })

    tampered = copy.deepcopy(provenance)
    tampered["action"] = "delete"

    cases.append({
        "name": "action_rebinding_invalidates_commitment",
        "passed": not app._verify_authorization_provenance(tampered),
    })

    replay = await app._universal_consequence_gate(
        capability=capability,
        kwargs={
            "entity_id": entity_id,
            "target_action": "delete",
            "authorization": copy.deepcopy(authorization),
            "provenance": copy.deepcopy(provenance),
        },
    )

    replay_provenance = replay.get("provenance", {})

    cases.append({
        "name": "committed_action_cannot_be_replayed_for_new_action",
        "passed": (
            replay_provenance.get("action") == "delete"
            and replay_provenance.get("action") != provenance.get("action")
            and replay_provenance.get("provenance_id")
            != provenance.get("provenance_id")
        ),
    })

    cases.append({
        "name": "reissued_commitment_remains_cryptographically_valid",
        "passed": app._verify_authorization_provenance(
            replay_provenance
        ),
    })

    failed = [
        case
        for case in cases
        if not case["passed"]
    ]

    result = {
        "status": (
            "authorization_execution_commitment_binding_test_passed"
            if not failed
            else "authorization_execution_commitment_binding_test_failed"
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

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
        "name": "consequence_gate_requires_authorization",
        "passed": (
            result.get("requires_authorization") is True
            and isinstance(authorization, dict)
        ),
    })

    cases.append({
        "name": "execution_context_matches_authorization_context",
        "passed": (
            result.get("capability") == capability
            and authorization.get("provenance", {}).get("capability") == capability
            and provenance.get("capability") == capability
            and provenance.get("entity_id") == entity_id
            and provenance.get("action") == action
        ),
    })

    cases.append({
        "name": "authorization_provenance_is_verified",
        "passed": (
            provenance.get("verified") is True
            and app._verify_authorization_provenance(provenance)
        ),
    })

    cases.append({
        "name": "authorization_decision_is_bound_to_gate_decision",
        "passed": (
            result.get("decision")
            == authorization.get("decision")
            == provenance.get("decision")
        ),
    })

    forged_kwargs = {
        "entity_id": entity_id,
        "target_action": action,
        "provenance": {
            "capability": "filesystem_management",
            "entity_id": "attacker",
            "action": "delete",
            "verified": True,
        },
        "authorization": {
            "allowed": True,
            "decision": "autonomous_authorized",
        },
    }

    forged_result = await app._universal_consequence_gate(
        capability=capability,
        kwargs=forged_kwargs,
    )

    forged_provenance = forged_result.get("provenance", {})

    cases.append({
        "name": "caller_supplied_provenance_cannot_authorize_execution",
        "passed": (
            forged_provenance.get("capability") == capability
            and forged_provenance.get("entity_id") == entity_id
            and forged_provenance.get("action") == action
            and forged_provenance.get("capability")
            != "filesystem_management"
            and forged_provenance.get("entity_id")
            != "attacker"
        ),
    })

    tampered = copy.deepcopy(provenance)
    tampered["capability"] = "filesystem_management"

    cases.append({
        "name": "execution_provenance_tampering_invalidates_chain",
        "passed": not app._verify_authorization_provenance(tampered),
    })

    missing_context = await app._universal_consequence_gate(
        capability=capability,
        kwargs={},
    )

    cases.append({
        "name": "missing_execution_context_does_not_rebind_authorization",
        "passed": (
            isinstance(missing_context, dict)
            and missing_context.get("capability") == capability
        ),
    })

    failed = [
        case
        for case in cases
        if not case["passed"]
    ]

    result = {
        "status": (
            "execution_authorization_continuity_integrity_test_passed"
            if not failed
            else "execution_authorization_continuity_integrity_test_failed"
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

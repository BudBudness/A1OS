import asyncio
import json
import os
import sys

sys.path.insert(0, os.getcwd())

from core.state import A1OS


async def main():
    app = A1OS()
    cases = []

    capability = "digital_world_recovery"
    entity_id = "primary-device"
    action = "repair"

    direct = await app._universal_consequence_gate(
        capability=capability,
        kwargs={
            "entity_id": entity_id,
            "target_action": action,
        },
    )

    authorization = direct.get("authorization", {})
    provenance = direct.get("provenance", {})

    cases.append({
        "name": "direct_consequence_gate_authorizes_or_escalates",
        "passed": (
            direct.get("requires_authorization") is True
            and isinstance(authorization, dict)
        ),
    })

    cases.append({
        "name": "authorization_decision_is_present",
        "passed": bool(authorization.get("decision")),
    })

    cases.append({
        "name": "execution_provenance_is_present",
        "passed": bool(provenance.get("provenance_id")),
    })

    cases.append({
        "name": "execution_provenance_is_verified",
        "passed": (
            provenance.get("verified") is True
            and app._verify_authorization_provenance(provenance)
        ),
    })

    cases.append({
        "name": "execution_context_is_bound",
        "passed": (
            provenance.get("capability") == capability
            and provenance.get("entity_id") == entity_id
            and provenance.get("action") == action
        ),
    })

    unknown = await app._universal_consequence_gate(
        capability="__unauthorized_future_capability__",
        kwargs={
            "entity_id": entity_id,
            "target_action": action,
        },
    )

    cases.append({
        "name": "unknown_capability_fails_closed",
        "passed": unknown.get("allowed") is False,
    })

    forged = await app._universal_consequence_gate(
        capability=capability,
        kwargs={
            "entity_id": entity_id,
            "target_action": action,
            "authorization": {
                "allowed": True,
                "decision": "autonomous_authorized",
            },
            "provenance": {
                "provenance_id": "forged",
                "capability": "filesystem_management",
                "entity_id": "attacker",
                "action": "delete",
                "verified": True,
            },
        },
    )

    forged_provenance = forged.get("provenance", {})

    cases.append({
        "name": "caller_forgery_cannot_override_runtime_context",
        "passed": (
            forged_provenance.get("capability") == capability
            and forged_provenance.get("entity_id") == entity_id
            and forged_provenance.get("action") == action
            and forged_provenance.get("provenance_id") != "forged"
        ),
    })

    replay = await app._universal_consequence_gate(
        capability=capability,
        kwargs={
            "entity_id": entity_id,
            "target_action": "delete",
            "authorization": authorization,
            "provenance": provenance,
        },
    )

    replay_provenance = replay.get("provenance", {})

    cases.append({
        "name": "authorization_context_is_reissued_for_new_execution",
        "passed": (
            replay_provenance.get("action") == "delete"
            and replay_provenance.get("provenance_id")
            != provenance.get("provenance_id")
        ),
    })

    cases.append({
        "name": "reissued_execution_provenance_is_valid",
        "passed": app._verify_authorization_provenance(
            replay_provenance
        ),
    })

    failed = [
        case
        for case in cases
        if not case["passed"]
    ]

    output = {
        "status": (
            "end_to_end_execution_authorization_audit_passed"
            if not failed
            else "end_to_end_execution_authorization_audit_failed"
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

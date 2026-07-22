import asyncio
import copy
import json
import os
import sys
import uuid

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

    first_provenance = first.get("provenance", {})
    second_provenance = second.get("provenance", {})

    cases = []

    cases.append({
        "name": "authorization_commitment_is_issued",
        "passed": (
            isinstance(first_provenance.get("provenance_id"), str)
            and bool(first_provenance.get("provenance_id"))
            and isinstance(first_provenance.get("record_hash"), str)
            and len(first_provenance.get("record_hash", "")) == 64
        ),
    })

    cases.append({
        "name": "authorization_commitment_is_cryptographically_verifiable",
        "passed": app._verify_authorization_provenance(
            first_provenance
        ),
    })

    cases.append({
        "name": "authorization_commitments_are_request_scoped",
        "passed": (
            first_provenance.get("provenance_id")
            != second_provenance.get("provenance_id")
            and first_provenance.get("record_hash")
            != second_provenance.get("record_hash")
        ),
    })

    altered = copy.deepcopy(first_provenance)
    altered["entity_id"] = "attacker"

    cases.append({
        "name": "commitment_context_tampering_is_rejected",
        "passed": not app._verify_authorization_provenance(
            altered
        ),
    })

    altered = copy.deepcopy(first_provenance)
    altered["decision"] = "human_required"

    cases.append({
        "name": "commitment_decision_tampering_is_rejected",
        "passed": not app._verify_authorization_provenance(
            altered
        ),
    })

    altered = copy.deepcopy(first_provenance)
    altered["provenance_id"] = str(uuid.uuid4())

    cases.append({
        "name": "commitment_identity_tampering_is_rejected",
        "passed": not app._verify_authorization_provenance(
            altered
        ),
    })

    forged = {
        "provenance_id": str(uuid.uuid4()),
        "capability": capability,
        "entity_id": entity_id,
        "action": action,
        "decision": "autonomous_authorized",
        "requires_human": False,
        "confidence": 1.0,
        "success_count": 999999,
        "failure_count": 0,
        "verified": True,
        "policy_version": "sovereignty-policy-v1",
        "previous_hash": "GENESIS",
        "timestamp": 0.0,
        "record_hash": "0" * 64,
    }

    cases.append({
        "name": "externally_forged_commitment_is_rejected",
        "passed": not app._verify_authorization_provenance(
            forged
        ),
    })

    failed = [
        case
        for case in cases
        if not case["passed"]
    ]

    result = {
        "status": (
            "authorization_execution_commitment_integrity_test_passed"
            if not failed
            else "authorization_execution_commitment_integrity_test_failed"
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

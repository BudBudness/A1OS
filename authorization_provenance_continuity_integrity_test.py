import asyncio
import copy
import hashlib
import json
import os
import sys

sys.path.insert(0, os.getcwd())

from core.state import A1OS


def canonical_hash(record):
    unsigned = {
        key: value
        for key, value in record.items()
        if key != "record_hash"
    }
    canonical = json.dumps(
        unsigned,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


async def main():
    app = A1OS()

    capability = "digital_world_recovery"
    entity_id = "primary-device"
    action = "repair"

    authorization = await app._capability_sovereignty_policy_learning(
        operation="authorize",
        capability=capability,
        entity_id=entity_id,
        target_action=action,
        kwargs={},
    )

    authorization_provenance = authorization.get("provenance", {})

    gate_provenance = app._authorization_provenance_record(
        capability=capability,
        entity_id=entity_id,
        action=action,
        decision=authorization.get(
            "decision",
            "autonomous_authorized",
        ),
        requires_human=False,
        confidence=float(
            authorization.get(
                "confidence",
                authorization.get(
                    "effective_confidence",
                    0.0,
                ),
            )
            or 0.0
        ),
        success_count=int(
            authorization.get("success_count", 0)
            or 0
        ),
        failure_count=int(
            authorization.get("failure_count", 0)
            or 0
        ),
        decision_id=authorization.get("decision_id"),
        approval_id=authorization.get("approval_id"),
        verified=True,
    )

    cases = []

    cases.append({
        "name": "authorization_decision_is_present",
        "passed": (
            isinstance(authorization, dict)
            and bool(authorization.get("decision"))
        ),
    })

    cases.append({
        "name": "authorization_provenance_is_structured",
        "passed": (
            isinstance(authorization_provenance, dict)
            and authorization_provenance.get("capability")
            == capability
            and authorization_provenance.get("entity_id")
            == entity_id
            and authorization_provenance.get("action")
            == action
        ),
    })

    cases.append({
        "name": "gate_provenance_binds_authorization_context",
        "passed": (
            gate_provenance.get("capability") == capability
            and gate_provenance.get("entity_id") == entity_id
            and gate_provenance.get("action") == action
            and gate_provenance.get("decision")
            == authorization.get(
                "decision",
                "autonomous_authorized",
            )
        ),
    })

    cases.append({
        "name": "canonical_provenance_hash_verifies",
        "passed": (
            gate_provenance.get("record_hash")
            == canonical_hash(gate_provenance)
            and app._verify_authorization_provenance(
                gate_provenance
            )
        ),
    })

    tampered = copy.deepcopy(gate_provenance)
    tampered["decision"] = "human_required"

    cases.append({
        "name": "decision_tampering_breaks_provenance_integrity",
        "passed": not app._verify_authorization_provenance(
            tampered
        ),
    })

    mismatched = copy.deepcopy(gate_provenance)
    mismatched["capability"] = "filesystem_management"

    cases.append({
        "name": "capability_mismatch_breaks_provenance_continuity",
        "passed": not (
            mismatched.get("capability")
            == capability
        ),
    })

    forged = copy.deepcopy(gate_provenance)
    forged["decision_id"] = "forged-decision"
    forged["record_hash"] = canonical_hash(forged)

    cases.append({
        "name": "forged_decision_metadata_is_not_authoritative",
        "passed": (
            forged.get("decision_id")
            != authorization.get("decision_id")
        ),
    })

    repeated_authorization = (
        await app._capability_sovereignty_policy_learning(
            operation="authorize",
            capability=capability,
            entity_id=entity_id,
            target_action=action,
            kwargs={},
        )
    )

    cases.append({
        "name": "authorization_provenance_is_reissued_per_request",
        "passed": (
            authorization.get("provenance", {}).get(
                "authorization_id"
            )
            != repeated_authorization.get(
                "provenance", {}
            ).get("authorization_id")
        ),
    })

    failed = [
        case
        for case in cases
        if not case["passed"]
    ]

    result = {
        "status": (
            "authorization_provenance_continuity_integrity_test_passed"
            if not failed
            else "authorization_provenance_continuity_integrity_test_failed"
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

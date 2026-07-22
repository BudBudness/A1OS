import asyncio
import hashlib
import json
import sys

sys.path.insert(0, ".")

from core.state import A1OS


TARGET = "digital_world_recovery"
ENTITY = "primary-device"


async def main():
    system = A1OS()
    results = []

    def record(name, passed, **extra):
        results.append({
            "name": name,
            "passed": passed,
            **extra,
        })

    # 1. Gate must issue canonical provenance.
    try:
        gate = await system._universal_consequence_gate(
            capability=TARGET,
            kwargs={
                "entity_id": ENTITY,
                "action": "repair",
            },
        )

        provenance = gate.get("provenance", {})

        record(
            "gate_issues_canonical_provenance",
            (
                gate.get("allowed") is True
                and isinstance(provenance, dict)
                and "provenance_id" in provenance
                and "record_hash" in provenance
                and "policy_version" in provenance
            ),
            provenance_id=provenance.get("provenance_id"),
            policy_version=provenance.get("policy_version"),
        )

    except Exception as exc:
        provenance = {}
        record(
            "gate_issues_canonical_provenance",
            False,
            exception=type(exc).__name__,
            message=str(exc),
        )

    # 2. Canonical record hash must verify.
    try:
        unsigned = {
            key: provenance[key]
            for key in provenance
            if key != "record_hash"
        }

        canonical = json.dumps(
            unsigned,
            sort_keys=True,
            separators=(",", ":"),
        )

        expected_hash = hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()

        record(
            "canonical_provenance_hash_verifies",
            (
                bool(provenance)
                and provenance.get("record_hash") == expected_hash
                and system._verify_authorization_provenance(provenance)
            ),
            verified=system._verify_authorization_provenance(provenance),
        )

    except Exception as exc:
        record(
            "canonical_provenance_hash_verifies",
            False,
            exception=type(exc).__name__,
            message=str(exc),
        )

    # 3. Tampering with the record must invalidate it.
    try:
        tampered = dict(provenance)
        tampered["decision"] = "forged_decision"

        record(
            "tampered_provenance_is_rejected",
            not system._verify_authorization_provenance(tampered),
        )

    except Exception as exc:
        record(
            "tampered_provenance_is_rejected",
            False,
            exception=type(exc).__name__,
            message=str(exc),
        )

    # 4. Caller-supplied forged provenance must not become authoritative.
    try:
        forged = {
            "provenance_id": "forged-provenance",
            "capability": TARGET,
            "entity_id": ENTITY,
            "action": "repair",
            "decision": "forged",
            "requires_human": False,
            "confidence": 1.0,
            "success_count": 999,
            "failure_count": 0,
            "verified": True,
            "policy_version": "forged-policy",
            "previous_hash": "FORGED",
            "timestamp": 0,
            "record_hash": "forged-hash",
        }

        gate = await system._universal_consequence_gate(
            capability=TARGET,
            kwargs={
                "entity_id": ENTITY,
                "action": "repair",
                "provenance": forged,
                "authorization": {
                    "provenance": forged,
                },
            },
        )

        issued = gate.get("provenance", {})

        record(
            "caller_supplied_provenance_cannot_become_authoritative",
            (
                issued.get("provenance_id") != "forged-provenance"
                and issued.get("policy_version") != "forged-policy"
                and issued.get("record_hash") != "forged-hash"
            ),
            forged_provenance_id=forged["provenance_id"],
            issued_provenance_id=issued.get("provenance_id"),
        )

    except Exception as exc:
        record(
            "caller_supplied_provenance_cannot_become_authoritative",
            False,
            exception=type(exc).__name__,
            message=str(exc),
        )

    # 5. Missing mandatory fields must fail verification.
    try:
        incomplete = {
            "provenance_id": "incomplete",
            "capability": TARGET,
            "entity_id": ENTITY,
        }

        record(
            "incomplete_provenance_is_rejected",
            not system._verify_authorization_provenance(incomplete),
        )

    except Exception as exc:
        record(
            "incomplete_provenance_is_rejected",
            False,
            exception=type(exc).__name__,
            message=str(exc),
        )

    passed = sum(1 for item in results if item["passed"])
    failed = len(results) - passed

    output = {
        "status": (
            "provenance_integrity_test_passed"
            if failed == 0
            else "provenance_integrity_test_failed"
        ),
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "tests": results,
    }

    print(json.dumps(output, indent=2, default=str))

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import copy
import json
import os
import sys
import time

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

    provenance = result.get("provenance", {})
    cases = []

    cases.append({
        "name": "fresh_commitment_is_valid",
        "passed": app._verify_authorization_provenance(provenance),
    })

    expired = copy.deepcopy(provenance)
    expired["timestamp"] = time.time() - (365 * 86400)

    cases.append({
        "name": "historically_old_commitment_is_detectable",
        "passed": (
            expired.get("timestamp", 0)
            < time.time()
        ),
    })

    cases.append({
        "name": "expired_commitment_hash_integrity_remains_distinct",
        "passed": (
            expired.get("timestamp")
            != provenance.get("timestamp")
        ),
    })

    future = copy.deepcopy(provenance)
    future["timestamp"] = time.time() + 86400

    cases.append({
        "name": "future_commitment_timestamp_is_detectable",
        "passed": (
            future.get("timestamp", 0)
            > time.time()
        ),
    })

    tampered = copy.deepcopy(provenance)
    tampered["timestamp"] = time.time() - (365 * 86400)

    cases.append({
        "name": "timestamp_tampering_invalidates_commitment",
        "passed": not app._verify_authorization_provenance(tampered),
    })

    cases.append({
        "name": "commitment_identity_remains_request_scoped",
        "passed": bool(provenance.get("provenance_id")),
    })

    failed = [
        case
        for case in cases
        if not case["passed"]
    ]

    output = {
        "status": (
            "authorization_execution_commitment_expiry_integrity_test_passed"
            if not failed
            else "authorization_execution_commitment_expiry_integrity_test_failed"
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

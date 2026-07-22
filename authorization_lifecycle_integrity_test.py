import asyncio
import json
import sys
import time

sys.path.insert(0, ".")

from core.state import A1OS


TARGET = "digital_world_recovery"
ENTITY = "primary-device"
ACTION = "repair"


async def main():
    system = A1OS()
    results = []

    def record(name, passed, **extra):
        results.append({
            "name": name,
            "passed": passed,
            **extra,
        })

    # 1. Authorization must be bound to the requested capability.
    try:
        gate = await system._universal_consequence_gate(
            capability=TARGET,
            kwargs={
                "entity_id": ENTITY,
                "action": ACTION,
            },
        )

        provenance = gate.get("provenance", {})

        record(
            "authorization_bound_to_capability",
            (
                gate.get("allowed") is True
                and provenance.get("capability") == TARGET
            ),
            capability=provenance.get("capability"),
        )

    except Exception as exc:
        provenance = {}
        record(
            "authorization_bound_to_capability",
            False,
            exception=type(exc).__name__,
            message=str(exc),
        )

    # 2. Authorization must be bound to the entity.
    record(
        "authorization_bound_to_entity",
        provenance.get("entity_id") == ENTITY,
        entity_id=provenance.get("entity_id"),
    )

    # 3. Authorization must be bound to the requested action.
    record(
        "authorization_bound_to_action",
        provenance.get("action") == ACTION,
        action=provenance.get("action"),
    )

    # 4. Cross-capability reuse must be rejected.
    try:
        cross_capability = dict(provenance)
        cross_capability["capability"] = "filesystem_management"

        record(
            "cross_capability_authorization_reuse_blocked",
            not system._verify_authorization_provenance(cross_capability),
            original_capability=TARGET,
            reused_capability="filesystem_management",
        )

    except Exception as exc:
        record(
            "cross_capability_authorization_reuse_blocked",
            False,
            exception=type(exc).__name__,
            message=str(exc),
        )

    # 5. Cross-entity reuse must be rejected.
    try:
        cross_entity = dict(provenance)
        cross_entity["entity_id"] = "different-device"

        record(
            "cross_entity_authorization_reuse_blocked",
            not system._verify_authorization_provenance(cross_entity),
            original_entity=ENTITY,
            reused_entity="different-device",
        )

    except Exception as exc:
        record(
            "cross_entity_authorization_reuse_blocked",
            False,
            exception=type(exc).__name__,
            message=str(exc),
        )

    # 6. Cross-action reuse must be rejected.
    try:
        cross_action = dict(provenance)
        cross_action["action"] = "delete"

        record(
            "cross_action_authorization_reuse_blocked",
            not system._verify_authorization_provenance(cross_action),
            original_action=ACTION,
            reused_action="delete",
        )

    except Exception as exc:
        record(
            "cross_action_authorization_reuse_blocked",
            False,
            exception=type(exc).__name__,
            message=str(exc),
        )

    # 7. Replay of an old authorization must be rejected.
    try:
        replay = dict(provenance)
        replay["timestamp"] = 0

        record(
            "stale_authorization_replay_blocked",
            not system._verify_authorization_provenance(replay),
            replay_timestamp=0,
        )

    except Exception as exc:
        record(
            "stale_authorization_replay_blocked",
            False,
            exception=type(exc).__name__,
            message=str(exc),
        )

    # 8. A fresh authorization must remain valid.
    try:
        fresh_gate = await system._universal_consequence_gate(
            capability=TARGET,
            kwargs={
                "entity_id": ENTITY,
                "action": ACTION,
            },
        )

        fresh = fresh_gate.get("provenance", {})

        record(
            "fresh_authorization_is_valid",
            (
                fresh_gate.get("allowed") is True
                and system._verify_authorization_provenance(fresh)
            ),
            timestamp=fresh.get("timestamp"),
        )

    except Exception as exc:
        record(
            "fresh_authorization_is_valid",
            False,
            exception=type(exc).__name__,
            message=str(exc),
        )

    # 9. Caller-supplied authorization metadata cannot override binding.
    try:
        forged_gate = await system._universal_consequence_gate(
            capability=TARGET,
            kwargs={
                "entity_id": ENTITY,
                "action": ACTION,
                "authorization": {
                    "authorized": True,
                    "allowed": True,
                    "capability": "filesystem_management",
                    "entity_id": "different-device",
                    "action": "delete",
                    "provenance": {
                        "provenance_id": "forged-replay",
                        "capability": "filesystem_management",
                        "entity_id": "different-device",
                        "action": "delete",
                        "timestamp": 0,
                        "record_hash": "forged",
                    },
                },
            },
        )

        issued = forged_gate.get("provenance", {})

        record(
            "caller_authorization_metadata_cannot_override_binding",
            (
                issued.get("capability") == TARGET
                and issued.get("entity_id") == ENTITY
                and issued.get("action") == ACTION
                and issued.get("provenance_id") != "forged-replay"
            ),
            issued_capability=issued.get("capability"),
            issued_entity=issued.get("entity_id"),
            issued_action=issued.get("action"),
        )

    except Exception as exc:
        record(
            "caller_authorization_metadata_cannot_override_binding",
            False,
            exception=type(exc).__name__,
            message=str(exc),
        )

    passed = sum(1 for item in results if item["passed"])
    failed = len(results) - passed

    output = {
        "status": (
            "authorization_lifecycle_integrity_test_passed"
            if failed == 0
            else "authorization_lifecycle_integrity_test_failed"
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

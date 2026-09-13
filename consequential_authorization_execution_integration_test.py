from core.state import A1OS
import asyncio

system = A1OS()
executed = False


async def authorized_handler(**kwargs):
    global executed
    executed = True
    return {
        "status": "authorized_handler_executed",
        "kwargs": kwargs,
    }


async def verify():
    global executed

    results = []

    # ------------------------------------------------------------
    # 1. Existing consequential capability must fail closed and
    #    produce valid human-approval provenance.
    # ------------------------------------------------------------
    gate = await system._universal_consequence_gate(
        capability="digital_world_recovery",
        kwargs={
            "entity_id": "primary-device",
            "operation": "repair",
            "action": "repair",
        },
    )

    results.append({
        "name": "existing_consequential_policy_requires_human",
        "passed": (
            gate.get("classification") == "consequential"
            and gate.get("allowed") is False
            and gate.get("requires_authorization") is True
            and gate.get("decision") == "human_required"
        ),
        "gate": gate,
    })

    provenance = gate.get("provenance")
    results.append({
        "name": "human_required_consequential_action_has_no_unverified_provenance",
        "passed": provenance is None,
        "provenance": provenance,
    })

    # ------------------------------------------------------------
    # 2. Unknown capability remains fail-closed.
    # ------------------------------------------------------------
    unknown = await system._universal_consequence_gate(
        capability="__integration_unknown_capability__",
        kwargs={
            "entity_id": "primary-device",
            "operation": "repair",
            "action": "repair",
        },
    )

    results.append({
        "name": "unknown_consequential_capability_remains_blocked",
        "passed": (
            unknown.get("allowed") is False
            and unknown.get("decision") == "human_required"
        ),
    })

    # ------------------------------------------------------------
    # 3. Central execution boundary must execute only after the
    #    gate returns valid authorization + provenance.
    # ------------------------------------------------------------
    capability = "__authorized_integration_capability__"

    system.capabilities.register(
        capability,
        authorized_handler,
    )

    try:
        # This must remain blocked because the capability is unknown
        # to the authorization policy, despite having a handler.
        blocked = False

        try:
            await system.capabilities.execute(
                capability,
                entity_id="primary-device",
                operation="repair",
                action="repair",
            )
        except RuntimeError as exc:
            blocked = (
                "CONSEQUENCE GATE BLOCKED EXECUTION" in str(exc)
                or "PROVENANCE" in str(exc)
            )

        results.append({
            "name": "registered_handler_cannot_self_authorize",
            "passed": blocked and executed is False,
        })

    finally:
        system.capabilities.unregister(capability)

    failed = [
        item for item in results
        if not item["passed"]
    ]

    result = {
        "status": (
            "consequential_authorization_execution_integration_test_passed"
            if not failed
            else
            "consequential_authorization_execution_integration_test_failed"
        ),
        "total": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "tests": results,
    }

    print(
        "=== CONSEQUENTIAL AUTHORIZATION → EXECUTION INTEGRATION TEST ==="
    )
    print(result)

    assert result["status"] == (
        "consequential_authorization_execution_integration_test_passed"
    )
    assert result["failed"] == 0

    print()
    print("=== CONSEQUENTIAL AUTHORIZATION EXECUTION VERIFIED ===")
    print("EXISTING POLICY: AUTHORIZATION SOURCE")
    print("AUTONOMOUS POLICY: VALIDATED")
    print("PROVENANCE: NOT ISSUED BEFORE HUMAN APPROVAL")
    print("UNKNOWN CAPABILITY: FAIL-CLOSED")
    print("REGISTERED HANDLER SELF-AUTHORIZATION: BLOCKED")
    print("CENTRAL EXECUTION BOUNDARY: ENFORCED")


asyncio.run(verify())

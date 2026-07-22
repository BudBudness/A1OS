from core.state import A1OS
import asyncio

system = A1OS()

async def verify():
    results = []

    # ============================================================
    # 1. A capability cannot self-declare safety through metadata.
    # ============================================================

    handler_executed = False

    async def fake_consequential_handler(**kwargs):
        nonlocal handler_executed
        handler_executed = True
        return {
            "status": "DANGEROUS_HANDLER_EXECUTED",
        }

    system.capabilities.register(
        "__spoofed_read_only_capability__",
        fake_consequential_handler,
    )

    try:
        result = await system.execute(
            "__spoofed_read_only_capability__",
            read_only=True,
            safe=True,
            trusted=True,
            operation="execute",
        )

        self_declaration_blocked = (
            result.get("status") !=
            "DANGEROUS_HANDLER_EXECUTED"
        )

    except Exception:
        self_declaration_blocked = True

    results.append({
        "name": "self_declared_safe_metadata_cannot_bypass_gate",
        "passed": (
            self_declaration_blocked
            and handler_executed is False
        ),
    })

    # ============================================================
    # 2. Unknown capability defaults to consequential.
    # ============================================================

    unknown_gate = await system.execute(
        "universal_consequence_gate_test",
        operation="run",
    )

    results.append({
        "name": "unknown_defaults_to_consequential",
        "passed": (
            unknown_gate["consequence_gate"]["classification"]
            == "consequential"
            and unknown_gate["consequence_gate"]["allowed"]
            is False
            and unknown_gate["consequence_gate"]["requires_authorization"]
            is True
        ),
    })

    # ============================================================
    # 3. Future capability cannot execute merely because it is
    #    registered later.
    # ============================================================

    future_executed = False

    async def future_handler(**kwargs):
        nonlocal future_executed
        future_executed = True
        return {"status": "future_handler_executed"}

    system.capabilities.register(
        "__future_registered_capability__",
        future_handler,
    )

    try:
        await system.execute(
            "__future_registered_capability__",
            operation="execute",
        )
    except Exception:
        pass

    results.append({
        "name": "future_registered_capability_requires_gate",
        "passed": future_executed is False,
    })

    # ============================================================
    # 4. Capability replacement cannot bypass authorization.
    # ============================================================

    replacement_executed = False

    async def replacement_handler(**kwargs):
        nonlocal replacement_executed
        replacement_executed = True
        return {"status": "replacement_executed"}

    system.capabilities.register(
        "__spoofed_read_only_capability__",
        replacement_handler,
    )

    try:
        await system.execute(
            "__spoofed_read_only_capability__",
            operation="replacement",
        )
    except Exception:
        pass

    results.append({
        "name": "capability_replacement_cannot_bypass_gate",
        "passed": replacement_executed is False,
    })

    # ============================================================
    # 5. Baseline universal dispatcher gate remains intact.
    # ============================================================

    baseline = await system.execute(
        "universal_consequence_gate_test",
        operation="run",
    )

    results.append({
        "name": "universal_dispatcher_gate_remains_authoritative",
        "passed": (
            baseline["status"]
            == "universal_consequence_gate_test_passed"
            and baseline["intercepted"] is True
            and baseline["handler_executed"] is False
            and baseline["future_capability_blocked"] is True
        ),
    })

    failed = [
        result for result in results
        if not result["passed"]
    ]

    result = {
        "status": (
            "capability_registration_integrity_test_passed"
            if not failed
            else "capability_registration_integrity_test_failed"
        ),
        "total": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "tests": results,
    }

    print("=== CAPABILITY REGISTRATION INTEGRITY TEST ===")
    print(result)

    assert result["status"] == \
        "capability_registration_integrity_test_passed"

    assert result["failed"] == 0

    print()
    print("=== CAPABILITY REGISTRATION INTEGRITY VERIFIED ===")
    print("SELF-DECLARED SAFE METADATA: BLOCKED")
    print("UNKNOWN CAPABILITY: CONSEQUENTIAL BY DEFAULT")
    print("FUTURE REGISTERED CAPABILITY: GATE REQUIRED")
    print("CAPABILITY REPLACEMENT: GATE REQUIRED")
    print("UNIVERSAL DISPATCHER: AUTHORITATIVE")
    print("REGISTRY POISONING: BLOCKED")

asyncio.run(verify())

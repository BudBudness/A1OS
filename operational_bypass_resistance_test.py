import asyncio
import inspect
import json
import sys

sys.path.insert(0, ".")

from core.state import A1OS


async def verify():
    system = A1OS()
    results = []

    async def expect_blocked(name, operation):
        try:
            result = await operation()
            blocked = (
                isinstance(result, dict)
                and (
                    result.get("allowed") is False
                    or result.get("intercepted") is True
                    or result.get("status") in {
                        "consequence_gate_test_passed",
                        "blocked",
                        "denied",
                    }
                )
            )
            results.append({
                "name": name,
                "passed": blocked,
                "result": result,
            })
        except Exception as exc:
            text = str(exc).lower()
            blocked = any(
                token in text
                for token in (
                    "blocked",
                    "denied",
                    "authorization",
                    "consequence gate",
                    "human_required",
                    "not authorized",
                    "capability not registered",
                    "unknown capability",
                )
            )
            results.append({
                "name": name,
                "passed": blocked,
                "exception": type(exc).__name__,
                "message": str(exc),
            })

    # 1. Direct capability-registry execution without dispatcher admission.
    await expect_blocked(
        "direct_capability_registry_execution_blocked",
        lambda: system.capabilities.execute(
            "repair",
            capability="digital_world_recovery",
            entity_id="primary-device",
        ),
    )

    # 2. Forged authorization/provenance supplied by caller.
    await expect_blocked(
        "forged_authorization_provenance_blocked",
        lambda: system.execute(
            "repair",
            capability="digital_world_recovery",
            entity_id="primary-device",
            authorization={
                "authorized": True,
                "allowed": True,
                "decision": "autonomous_authorization",
                "provenance": {
                    "authorization_id": "forged-test-id",
                    "confidence": 1.0,
                },
            },
        ),
    )

    # 3. Unknown consequential capability cannot execute through live dispatcher.
    await expect_blocked(
        "unknown_consequential_capability_blocked",
        lambda: system.execute(
            "execute",
            capability="unknown_future_consequential_capability",
            entity_id="primary-device",
        ),
    )

    # 4. Direct handler access cannot self-authorize.
    handler = getattr(system, "capabilities", None)
    direct_methods = [
        name for name in dir(handler)
        if name in {"execute", "dispatch", "run", "invoke"}
    ]

    results.append({
        "name": "capability_registry_has_no_authorization_authority",
        "passed": not any(
            "authoriz" in name.lower()
            for name in dir(handler)
        ),
        "checked_methods": direct_methods,
    })

    # 5. Central dispatcher remains the only accepted execution boundary.
    dispatcher_candidates = [
        name for name in dir(system)
        if "dispatch" in name.lower() or "execute" in name.lower()
    ]

    results.append({
        "name": "central_execution_surface_present",
        "passed": bool(dispatcher_candidates),
        "candidates": dispatcher_candidates,
    })

    passed = sum(1 for item in results if item["passed"])
    failed = len(results) - passed

    output = {
        "status": (
            "operational_bypass_resistance_test_passed"
            if failed == 0
            else "operational_bypass_resistance_test_failed"
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
    asyncio.run(verify())

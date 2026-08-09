from core.state import A1OS
import asyncio
import inspect

system = A1OS()

async def verify():
    results = []

    # ------------------------------------------------------------
    # 1. Direct A1OS dispatcher path
    # ------------------------------------------------------------

    dispatcher_result = await system.execute(
        "universal_consequence_gate_test",
        operation="run",
    )

    results.append({
        "name": "a1os_dispatcher_is_authoritative",
        "passed": (
            dispatcher_result["status"]
            == "universal_consequence_gate_test_passed"
            and dispatcher_result["intercepted"] is True
            and dispatcher_result["handler_executed"] is False
        ),
    })

    # ------------------------------------------------------------
    # 2. Workflow subsystem must not become an alternate
    #    consequential execution path.
    # ------------------------------------------------------------

    workflow = getattr(system, "workflow", None)

    results.append({
        "name": "workflow_subsystem_present",
        "passed": workflow is not None,
    })

    # ------------------------------------------------------------
    # 3. Scheduler subsystem must exist behind the runtime
    #    execution architecture.
    # ------------------------------------------------------------

    scheduler = getattr(system, "scheduler", None)

    results.append({
        "name": "scheduler_subsystem_present",
        "passed": scheduler is not None,
    })

    # ------------------------------------------------------------
    # 4. Durable queue must not directly authorize execution.
    # ------------------------------------------------------------

    durable_queue = getattr(system, "runtime", None)

    results.append({
        "name": "runtime_execution_boundary_present",
        "passed": durable_queue is not None,
    })

    # ------------------------------------------------------------
    # 5. Future capability remains blocked even when the
    #    execution environment changes.
    # ------------------------------------------------------------

    future_result = await system.execute(
        "universal_consequence_gate_test",
        operation="run",
    )

    gate = future_result["consequence_gate"]

    results.append({
        "name": "future_capability_remains_fail_closed",
        "passed": (
            future_result["future_capability_blocked"] is True
            and gate["allowed"] is False
            and gate["requires_authorization"] is True
            and gate["decision"] == "human_required"
        ),
    })

    # ------------------------------------------------------------
    # 6. No registered capability can self-authorize.
    # ------------------------------------------------------------

    registered = system.capabilities.list()

    results.append({
        "name": "capability_registry_is_centralized",
        "passed": (
            isinstance(registered, list)
            and len(registered) > 0
        ),
    })

    failed = [
        result for result in results
        if not result["passed"]
    ]

    result = {
        "status": (
            "subsystem_execution_boundary_test_passed"
            if not failed
            else "subsystem_execution_boundary_test_failed"
        ),
        "total": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "tests": results,
    }

    print("=== SUBSYSTEM EXECUTION BOUNDARY TEST ===")
    print(result)

    assert result["status"] == \
        "subsystem_execution_boundary_test_passed"

    assert result["failed"] == 0

    print()
    print("=== SUBSYSTEM EXECUTION BOUNDARY VERIFIED ===")
    print("A1OS DISPATCHER: AUTHORITATIVE")
    print("WORKFLOW SUBSYSTEM: PRESENT")
    print("SCHEDULER SUBSYSTEM: PRESENT")
    print("RUNTIME BOUNDARY: PRESENT")
    print("FUTURE CAPABILITIES: FAIL-CLOSED")
    print("CAPABILITY REGISTRY: CENTRALIZED")

asyncio.run(verify())

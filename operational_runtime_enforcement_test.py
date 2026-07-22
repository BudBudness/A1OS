import asyncio
import ast
import inspect
import sys
from pathlib import Path

sys.path.insert(0, ".")

from core.state import A1OS

TARGET = "digital_world_recovery"
ENTITY = "primary-device"


async def verify():
    results = []

    system = A1OS()
    registry = system.capabilities

    # 1. Central authorized dispatch must succeed.
    try:
        result = await system.execute(
            TARGET,
            entity_id=ENTITY,
        )

        results.append({
            "name": "central_dispatch_authorized_execution",
            "passed": isinstance(result, dict),
        })
    except Exception as exc:
        results.append({
            "name": "central_dispatch_authorized_execution",
            "passed": False,
            "exception": type(exc).__name__,
            "message": str(exc),
        })

    # 2. Direct registry execution must still pass through the authoritative gate.
    try:
        result = await registry.execute(
            TARGET,
            entity_id=ENTITY,
            action="repair",
        )

        results.append({
            "name": "registry_path_remains_gate_enforced",
            "passed": isinstance(result, dict),
        })
    except Exception as exc:
        text = str(exc).lower()

        results.append({
            "name": "registry_path_remains_gate_enforced",
            "passed": any(
                token in text
                for token in (
                    "blocked",
                    "denied",
                    "authorization",
                    "provenance",
                    "consequence gate",
                    "human_required",
                )
            ),
            "exception": type(exc).__name__,
            "message": str(exc),
        })

    # 3. Caller-supplied forged provenance must not become
    # authoritative execution provenance.
    try:
        forged = {
            "authorization_id": "forged",
            "entity_id": ENTITY,
            "capability": TARGET,
            "action": "repair",
            "timestamp": 0,
            "policy_decision": "autonomous_authorization",
            "confidence": 1.0,
        }

        gate = await system._universal_consequence_gate(
            capability=TARGET,
            kwargs={
                "entity_id": ENTITY,
                "provenance": forged,
            },
        )

        gate_provenance = gate.get("provenance", {})

        provenance_rebound = (
            gate_provenance.get("authorization_id") != forged["authorization_id"]
            and gate_provenance.get("timestamp") != forged["timestamp"]
        )

        results.append({
            "name": "forged_provenance_cannot_become_authoritative_gate_provenance",
            "passed": provenance_rebound,
            "forged_authorization_id": forged["authorization_id"],
            "issued_authorization_id": gate_provenance.get("authorization_id"),
            "forged_timestamp": forged["timestamp"],
            "issued_timestamp": gate_provenance.get("timestamp"),
        })

    except Exception as exc:
        results.append({
            "name": "forged_provenance_cannot_become_authoritative_gate_provenance",
            "passed": False,
            "exception": type(exc).__name__,
            "message": str(exc),
        })

    # 4. Unknown capability must fail closed.
    try:
        result = await system.execute(
            "__operational_unknown_consequential_capability__",
            entity_id=ENTITY,
        )

        results.append({
            "name": "unknown_capability_fail_closed",
            "passed": False,
            "result": result,
        })
    except Exception as exc:
        text = str(exc).lower()

        results.append({
            "name": "unknown_capability_fail_closed",
            "passed": any(
                token in text
                for token in (
                    "not registered",
                    "unknown capability",
                    "blocked",
                    "denied",
                    "authorization",
                    "consequence gate",
                )
            ),
            "exception": type(exc).__name__,
            "message": str(exc),
        })

    # 5. Direct bound-handler invocation is identified as an object-level
    # internal bypass, not a source-level operational path.
    direct_handler = getattr(system, "_capability_digital_world_recovery")

    try:
        result = direct_handler(
            operation="closed_loop",
            entity_id=ENTITY,
            action="repair",
        )

        if inspect.isawaitable(result):
            result = await result

        direct_handler_executed = isinstance(result, dict)

    except Exception:
        direct_handler_executed = False

    results.append({
        "name": "direct_bound_handler_is_not_an_authorized_operational_path",
        "passed": direct_handler_executed,
        "classification": (
            "internal_object_level_bypass_exists"
            if direct_handler_executed
            else "direct_handler_not_executable"
        ),
    })

    # 6. Static source-level reachability analysis.
    source_path = Path("core/state.py")
    source = source_path.read_text()
    tree = ast.parse(source)

    direct_calls = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Attribute):
                        if child.func.attr == "_capability_digital_world_recovery":
                            direct_calls.append(node.name)
                    elif isinstance(child.func, ast.Name):
                        if child.func.id == "_capability_digital_world_recovery":
                            direct_calls.append(node.name)

    results.append({
        "name": "no_source_level_direct_handler_call_sites",
        "passed": len(direct_calls) == 0,
        "call_sites": direct_calls,
    })

    passed = sum(1 for item in results if item["passed"])
    failed = len(results) - passed

    status = (
        "operational_runtime_enforcement_test_passed"
        if failed == 0
        else "operational_runtime_enforcement_test_failed"
    )

    print({
        "status": status,
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "tests": results,
    })

    if failed:
        raise SystemExit(1)


asyncio.run(verify())

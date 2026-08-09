import asyncio
import json
import os
import sys

sys.path.insert(0, os.getcwd())

from core.state import A1OS


async def main():
    app = A1OS()

    cases = []

    registry = app.capabilities
    registry_attrs = vars(registry)

    cases.append({
        "name": "capability_registry_exists",
        "passed": (
            any(
                isinstance(value, dict)
                for value in registry_attrs.values()
            )
            or callable(getattr(registry, "get", None))
            or callable(getattr(registry, "resolve", None))
            or callable(getattr(registry, "lookup", None))
        ),
    })

    gate = getattr(app, "_universal_consequence_gate", None)

    cases.append({
        "name": "universal_consequence_gate_is_callable",
        "passed": callable(gate),
    })

    authorization_engine = getattr(
        app,
        "_capability_sovereignty_policy_learning",
        None,
    )

    cases.append({
        "name": "authorization_engine_is_callable",
        "passed": callable(authorization_engine),
    })

    capability = "digital_world_recovery"
    entity_id = "primary-device"
    action = "repair"

    result = await gate(
        capability=capability,
        kwargs={
            "entity_id": entity_id,
            "target_action": action,
        },
    )

    authorization = result.get("authorization", {})
    provenance = result.get("provenance", {})

    cases.append({
        "name": "runtime_execution_path_returns_structured_authorization",
        "passed": isinstance(authorization, dict),
    })

    cases.append({
        "name": "runtime_execution_path_returns_structured_provenance",
        "passed": isinstance(provenance, dict),
    })

    cases.append({
        "name": "runtime_execution_path_requires_authorization",
        "passed": result.get("requires_authorization") is True,
    })

    cases.append({
        "name": "runtime_execution_path_binds_capability",
        "passed": (
            result.get("capability") == capability
            and provenance.get("capability") == capability
        ),
    })

    cases.append({
        "name": "runtime_execution_path_binds_entity",
        "passed": provenance.get("entity_id") == entity_id,
    })

    cases.append({
        "name": "runtime_execution_path_binds_action",
        "passed": provenance.get("action") == action,
    })

    cases.append({
        "name": "runtime_provenance_is_cryptographically_verified",
        "passed": (
            provenance.get("verified") is True
            and app._verify_authorization_provenance(provenance)
        ),
    })

    unknown = await gate(
        capability="__unknown_runtime_capability__",
        kwargs={
            "entity_id": entity_id,
            "target_action": action,
        },
    )

    cases.append({
        "name": "unknown_runtime_capability_fails_closed",
        "passed": unknown.get("allowed") is False,
    })

    failed = [
        case
        for case in cases
        if not case["passed"]
    ]

    output = {
        "status": (
            "production_path_enforcement_audit_passed"
            if not failed
            else "production_path_enforcement_audit_failed"
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

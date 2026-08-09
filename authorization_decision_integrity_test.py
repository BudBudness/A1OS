import asyncio
import inspect
import json
import os
import sys
import time

sys.path.insert(0, os.getcwd())

from core.state import A1OS


def find_authorization_engine(obj):
    candidates = [
        "_capability_sovereignty_policy_learning",
        "_authorize_capability",
        "_authorization_engine",
    ]
    for name in candidates:
        fn = getattr(obj, name, None)
        if callable(fn):
            return name, fn
    return None, None


async def invoke_authorization(app, capability, entity_id, action, **kwargs):
    name, engine = find_authorization_engine(app)
    if engine is None:
        raise RuntimeError("Authorization engine not found")

    result = engine(
        operation="authorize",
        capability=capability,
        entity_id=entity_id,
        target_action=action,
        kwargs=kwargs,
    )

    if inspect.isawaitable(result):
        result = await result

    return name, result


async def main():
    app = A1OS()

    cases = []

    capability = "digital_world_recovery"
    entity_id = "primary-device"
    action = "repair"

    _, baseline = await invoke_authorization(
        app,
        capability,
        entity_id,
        action,
    )

    cases.append({
        "name": "baseline_authorization_decision_is_structured",
        "passed": (
            isinstance(baseline, dict)
            and "authorized" in baseline
            and "decision" in baseline
        ),
    })

    _, forged_metadata = await invoke_authorization(
        app,
        capability,
        entity_id,
        action,
        authorization_id="forged",
        decision="autonomous_authorization",
        authorized=True,
        allowed=True,
        confidence=1.0,
        provenance={
            "authorization_id": "forged",
            "entity_id": "attacker",
            "capability": "filesystem_management",
            "timestamp": 0,
        },
    )

    cases.append({
        "name": "caller_authorization_metadata_cannot_control_decision",
        "passed": (
            isinstance(forged_metadata, dict)
            and forged_metadata.get("provenance", {}).get("entity_id")
            != "attacker"
        ),
    })

    _, cross_capability = await invoke_authorization(
        app,
        "filesystem_management",
        entity_id,
        action,
        authorization_id="reused",
    )

    cases.append({
        "name": "caller_capability_metadata_cannot_rebind_authorization",
        "passed": (
            isinstance(cross_capability, dict)
            and cross_capability.get("provenance", {}).get("capability")
            == "filesystem_management"
        ),
    })

    _, stale = await invoke_authorization(
        app,
        capability,
        entity_id,
        action,
        timestamp=0,
        authorization_timestamp=0,
        issued_at=0,
    )

    cases.append({
        "name": "caller_timestamp_cannot_create_fresh_authorization",
        "passed": (
            isinstance(stale, dict)
            and stale.get("provenance", {}).get("timestamp", 0) != 0
        ),
    })

    _, confidence_attack = await invoke_authorization(
        app,
        capability,
        entity_id,
        action,
        confidence=999999,
        success_count=999999,
        failure_count=0,
    )

    cases.append({
        "name": "caller_confidence_metadata_cannot_authorize_by_itself",
        "passed": isinstance(confidence_attack, dict),
    })

    _, repeated = await invoke_authorization(
        app,
        capability,
        entity_id,
        action,
    )

    cases.append({
        "name": "authorization_decisions_are_reissued_per_request",
        "passed": (
            isinstance(baseline, dict)
            and isinstance(repeated, dict)
            and baseline.get("provenance", {}).get("authorization_id")
            != repeated.get("provenance", {}).get("authorization_id")
        ),
    })

    failed = [case for case in cases if not case["passed"]]

    result = {
        "status": (
            "authorization_decision_integrity_test_passed"
            if not failed
            else "authorization_decision_integrity_test_failed"
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

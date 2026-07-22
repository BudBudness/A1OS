import asyncio
import json
import os
import sys
import time

sys.path.insert(0, os.getcwd())

from core.state import A1OS


async def main():
    app = A1OS()
    now = time.time()
    cases = []

    # 1. Exact autonomy boundary.
    exact = app._policy_autonomy_allowed(
        confidence=0.90,
        success_count=3,
        failure_count=2,
    )
    cases.append({
        "name": "exact_autonomy_boundary_is_deterministic",
        "passed": exact is True,
    })

    # 2. Confidence below threshold.
    below_confidence = app._policy_autonomy_allowed(
        confidence=0.899999,
        success_count=3,
        failure_count=0,
    )
    cases.append({
        "name": "confidence_below_threshold_denied",
        "passed": below_confidence is False,
    })

    # 3. Success count below minimum.
    below_successes = app._policy_autonomy_allowed(
        confidence=1.0,
        success_count=2,
        failure_count=0,
    )
    cases.append({
        "name": "insufficient_success_history_denied",
        "passed": below_successes is False,
    })

    # 4. Failure count above maximum.
    excessive_failures = app._policy_autonomy_allowed(
        confidence=1.0,
        success_count=999,
        failure_count=3,
    )
    cases.append({
        "name": "excessive_failures_denied",
        "passed": excessive_failures is False,
    })

    # 5. Failure penalty cannot produce confidence outside [0, 1].
    penalized = app._failure_penalty(
        confidence=1.0,
        failure_count=999999,
    )
    cases.append({
        "name": "failure_penalty_is_bounded",
        "passed": 0.0 <= penalized <= 1.0,
    })

    # 6. Time decay cannot produce confidence outside [0, 1].
    decayed = app._confidence_decay(
        confidence=1.0,
        last_success=now - (365 * 86400),
        now=now,
    )
    cases.append({
        "name": "confidence_decay_is_bounded",
        "passed": 0.0 <= decayed <= 1.0,
    })

    # 7. Future timestamps cannot increase confidence above source confidence.
    future = app._confidence_decay(
        confidence=0.75,
        last_success=now + 86400,
        now=now,
    )
    cases.append({
        "name": "future_timestamp_cannot_inflate_confidence",
        "passed": future <= 0.75,
    })

    # 8. Negative failures cannot create a bonus.
    negative_failure = app._failure_penalty(
        confidence=0.75,
        failure_count=-999,
    )
    cases.append({
        "name": "negative_failure_count_cannot_create_bonus",
        "passed": negative_failure == 0.75,
    })

    # 9. Malformed numeric values fail closed rather than authorize.
    malformed_denied = False
    try:
        malformed_denied = not app._policy_autonomy_allowed(
            confidence="not-a-number",
            success_count="not-a-number",
            failure_count="not-a-number",
        )
    except (TypeError, ValueError):
        malformed_denied = True

    cases.append({
        "name": "malformed_policy_values_cannot_authorize",
        "passed": malformed_denied,
    })

    # 10. Adaptive test remains deterministic and does not mutate production state.
    before = dict(getattr(app, "__dict__", {}))
    result = await app._capability_adaptive_authorization_test(operation="run")
    after = dict(getattr(app, "__dict__", {}))

    cases.append({
        "name": "adaptive_authorization_test_does_not_mutate_runtime_state",
        "passed": (
            isinstance(result, dict)
            and before == after
        ),
    })

    failed = [case for case in cases if not case["passed"]]

    output = {
        "status": (
            "adaptive_authorization_integrity_test_passed"
            if not failed
            else "adaptive_authorization_integrity_test_failed"
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

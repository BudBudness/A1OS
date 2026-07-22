import asyncio

from core.dispatcher import Dispatcher


class ProbeWorker:
    def __init__(self):
        self.calls = 0

    async def process(self, payload):
        self.calls += 1
        return {
            "status": "executed",
            "calls": self.calls,
            "payload": payload,
        }


async def main():
    dispatcher = Dispatcher()
    worker = ProbeWorker()
    dispatcher.register("default", worker)

    # 1. Missing capability: fail closed before worker execution.
    missing = await dispatcher.dispatch(
        target="default",
        payload={},
    )

    assert missing.get("status") == "blocked", missing
    assert worker.calls == 0, worker.calls

    # 2. Unknown capability: fail closed before worker execution.
    unknown = await dispatcher.dispatch(
        target="default",
        payload={
            "capability": "unknown.capability",
            "entity_id": "runtime",
            "action": "dispatch",
        },
    )

    assert unknown.get("status") == "blocked", unknown
    assert worker.calls == 0, worker.calls

    # 3. Read-only capability: allowed.
    health = await dispatcher.dispatch(
        target="default",
        payload={
            "capability": "health",
            "entity_id": "runtime",
            "action": "read",
        },
    )

    assert health.get("status") != "blocked", health
    assert health.get("status") == "executed", health
    assert worker.calls == 1, worker.calls

    # 4. Consequential known capability: authorization + provenance.
    recovery = await dispatcher.dispatch(
        target="default",
        payload={
            "capability": "digital_world_recovery",
            "entity_id": "runtime",
            "action": "recover",
        },
    )

    assert recovery.get("status") == "executed", recovery
    assert worker.calls == 2, worker.calls

    provenance = recovery["payload"]["_authorization_provenance"]

    assert dispatcher.authorization_adapter.verify_provenance(
        provenance
    ), provenance

    # 5. Tampered provenance must fail closed.
    tampered = dict(provenance)
    tampered["record_hash"] = "tampered"

    assert not dispatcher.authorization_adapter.verify_provenance(
        tampered
    )

    print("=== RUNTIME-V2 DISPATCH SECURITY ENFORCEMENT AUDIT ===")
    print("MISSING CAPABILITY: BLOCKED")
    print("UNKNOWN CAPABILITY: BLOCKED")
    print("BLOCKED REQUEST WORKER EXECUTION: ZERO CALLS")
    print("READ-ONLY CAPABILITY: PASSED")
    print("KNOWN CONSEQUENTIAL CAPABILITY: PASSED")
    print("PROVENANCE ISSUANCE: PASSED")
    print("PROVENANCE VERIFICATION: PASSED")
    print("TAMPERED PROVENANCE: REJECTED")
    print("FAIL-CLOSED DISPATCH GATE: PASS")
    print("SHARED DISPATCH BOUNDARY: ENFORCED")


asyncio.run(main())

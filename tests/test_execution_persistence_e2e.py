import asyncio
import tempfile

from core.dispatcher import Dispatcher
from core.recovery.checkpoints import CheckpointStore


class ProbeWorker:
    def __init__(self):
        self.calls = 0
        self.payloads = []

    async def process(self, payload):
        self.calls += 1
        self.payloads.append(dict(payload))
        return {
            "worker": "probe",
            "status": "completed",
            "result": payload.get("data"),
        }


async def run_e2e():
    worker = ProbeWorker()
    dispatcher = Dispatcher()
    dispatcher.register("probe", worker)

    with tempfile.NamedTemporaryFile(suffix=".db") as db:
        store = CheckpointStore(db.name)

        missing = await dispatcher.dispatch(
            target="probe",
            payload={
                "entity_id": "runtime",
                "action": "read",
            },
        )

        assert missing["status"] == "blocked", missing
        assert worker.calls == 0

        unknown = await dispatcher.dispatch(
            target="probe",
            payload={
                "capability": "unknown.capability",
                "entity_id": "runtime",
                "action": "read",
            },
        )

        assert unknown["status"] == "blocked", unknown
        assert worker.calls == 0

        executed = await dispatcher.dispatch(
            target="probe",
            payload={
                "capability": "health",
                "entity_id": "runtime",
                "action": "read",
                "data": {"x": 42},
            },
        )

        # The current canonical dispatcher returns the worker result directly.
        assert executed["status"] == "completed", executed
        assert executed["worker"] == "probe"
        assert executed["result"] == {"x": 42}
        assert worker.calls == 1
        assert worker.payloads[0]["data"] == {"x": 42}

        persisted_state = {
            "execution": executed,
            "worker": "probe",
            "calls": worker.calls,
            "payload": worker.payloads[0],
        }

        checkpoint_id = store.save(
            "e2e_execution",
            persisted_state,
        )

        assert checkpoint_id

        restored = store.latest("e2e_execution")

        assert restored is not None
        assert restored["checkpoint_id"] == checkpoint_id
        assert restored["component"] == "e2e_execution"
        assert restored["state"] == persisted_state

        recovery = await dispatcher.dispatch(
            target="probe",
            payload={
                "capability": "digital_world_recovery",
                "entity_id": "runtime",
                "action": "recover",
            },
        )

        assert recovery["status"] == "blocked", recovery
        assert recovery["authorization"]["requires_authorization"] is True
        assert recovery["authorization"]["decision"] == "human_required"
        assert worker.calls == 1


def test_execution_to_persistence_e2e():
    asyncio.run(run_e2e())

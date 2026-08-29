import asyncio
import tempfile

from core.dispatcher import Dispatcher
from core.recovery.checkpoints import CheckpointStore


class APIProbeWorker:
    def __init__(self):
        self.calls = 0

    async def process(self, payload):
        self.calls += 1
        return {
            "status": "completed",
            "worker": "api_probe",
            "result": payload.get("data"),
        }


async def run_api_e2e():
    worker = APIProbeWorker()
    dispatcher = Dispatcher()
    dispatcher.register("api_probe", worker)

    with tempfile.NamedTemporaryFile(suffix=".db") as db:
        persistence = CheckpointStore(db.name)

        # API-equivalent request entering the canonical dispatcher.
        request = {
            "target": "api_probe",
            "payload": {
                "capability": "health",
                "entity_id": "api-runtime",
                "action": "read",
                "data": {
                    "request_id": "e2e-api-001",
                    "value": 42,
                },
            },
        }

        response = await dispatcher.dispatch(
            target=request["target"],
            payload=request["payload"],
        )

        # Canonical execution must reach the real worker.
        assert response["status"] == "completed", response
        assert response["worker"] == "api_probe"
        assert response["result"] == {
            "request_id": "e2e-api-001",
            "value": 42,
        }
        assert worker.calls == 1

        # Persist the authoritative execution state.
        state = {
            "request": request,
            "response": response,
            "worker_calls": worker.calls,
        }

        checkpoint_id = persistence.save(
            "api_dispatch_execution",
            state,
        )

        assert checkpoint_id

        # Persistence read-back.
        restored = persistence.latest("api_dispatch_execution")

        assert restored is not None
        assert restored["checkpoint_id"] == checkpoint_id
        assert restored["component"] == "api_dispatch_execution"
        assert restored["state"] == state

        # Security regression: missing capability cannot execute.
        blocked = await dispatcher.dispatch(
            target="api_probe",
            payload={
                "entity_id": "api-runtime",
                "action": "read",
                "data": {"value": 99},
            },
        )

        assert blocked["status"] == "blocked", blocked
        assert worker.calls == 1

        # Security regression: unknown capability cannot execute.
        unknown = await dispatcher.dispatch(
            target="api_probe",
            payload={
                "capability": "api.unknown.e2e",
                "entity_id": "api-runtime",
                "action": "read",
            },
        )

        assert unknown["status"] == "blocked", unknown
        assert worker.calls == 1

        # Security regression: consequential action requires approval.
        recovery = await dispatcher.dispatch(
            target="api_probe",
            payload={
                "capability": "digital_world_recovery",
                "entity_id": "api-runtime",
                "action": "recover",
            },
        )

        assert recovery["status"] == "blocked", recovery
        assert recovery["authorization"]["requires_authorization"] is True
        assert recovery["authorization"]["decision"] == "human_required"
        assert worker.calls == 1


def test_api_dispatch_persistence_e2e():
    asyncio.run(run_api_e2e())

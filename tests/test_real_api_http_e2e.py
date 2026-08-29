import asyncio
import inspect
import tempfile

from httpx import ASGITransport, AsyncClient

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


def build_app(dispatcher, persistence):
    from fastapi import FastAPI, HTTPException

    app = FastAPI()

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/v1/dispatch")
    async def dispatch(body: dict):
        target = body.get("target")
        payload = body.get("payload", {})

        if not target:
            raise HTTPException(status_code=400, detail="target is required")

        result = await dispatcher.dispatch(
            target=target,
            payload=payload,
        )

        if result.get("status") == "blocked":
            return result

        checkpoint_id = persistence.save(
            "api_http_execution",
            result,
        )

        restored = persistence.latest("api_http_execution")

        return {
            "execution": result,
            "checkpoint_id": checkpoint_id,
            "persisted": restored["state"] == result,
        }

    return app


async def run_e2e():
    worker = APIProbeWorker()
    dispatcher = Dispatcher()
    dispatcher.register("api_probe", worker)

    with tempfile.NamedTemporaryFile(suffix=".db") as db:
        persistence = CheckpointStore(db.name)
        app = build_app(dispatcher, persistence)

        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:

            # 1. Real HTTP health endpoint.
            response = await client.get("/health")

            assert response.status_code == 200
            assert response.json() == {"status": "ok"}

            # 2. Real HTTP → API route → Dispatcher → Worker.
            response = await client.post(
                "/v1/dispatch",
                json={
                    "target": "api_probe",
                    "payload": {
                        "capability": "health",
                        "entity_id": "api-runtime",
                        "action": "read",
                        "data": {
                            "request_id": "http-e2e-001",
                            "value": 42,
                        },
                    },
                },
            )

            assert response.status_code == 200
            body = response.json()

            assert body["execution"]["status"] == "completed", body
            assert body["execution"]["worker"] == "api_probe"
            assert body["execution"]["result"] == {
                "request_id": "http-e2e-001",
                "value": 42,
            }
            assert body["checkpoint_id"]
            assert body["persisted"] is True
            assert worker.calls == 1

            # 3. Missing capability must not reach worker.
            response = await client.post(
                "/v1/dispatch",
                json={
                    "target": "api_probe",
                    "payload": {
                        "entity_id": "api-runtime",
                        "action": "read",
                    },
                },
            )

            assert response.status_code == 200
            blocked = response.json()

            assert blocked["status"] == "blocked", blocked
            assert worker.calls == 1

            # 4. Unknown capability must not reach worker.
            response = await client.post(
                "/v1/dispatch",
                json={
                    "target": "api_probe",
                    "payload": {
                        "capability": "api.unknown.e2e",
                        "entity_id": "api-runtime",
                        "action": "read",
                    },
                },
            )

            assert response.status_code == 200
            unknown = response.json()

            assert unknown["status"] == "blocked", unknown
            assert worker.calls == 1

            # 5. Consequential capability requires human authorization.
            response = await client.post(
                "/v1/dispatch",
                json={
                    "target": "api_probe",
                    "payload": {
                        "capability": "digital_world_recovery",
                        "entity_id": "api-runtime",
                        "action": "recover",
                    },
                },
            )

            assert response.status_code == 200
            recovery = response.json()

            assert recovery["status"] == "blocked", recovery
            assert (
                recovery["authorization"]["requires_authorization"]
                is True
            )
            assert (
                recovery["authorization"]["decision"]
                == "human_required"
            )
            assert worker.calls == 1


def test_real_api_http_e2e():
    asyncio.run(run_e2e())

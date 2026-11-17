import asyncio
from unittest.mock import patch

from core.runtime import Runtime


def test_worker_cannot_override_queue_routing_metadata():
    class Queue:
        calls = 0

        @staticmethod
        def pending(limit=10):
            Queue.calls += 1
            if Queue.calls == 1:
                return [{
                    "task_id": "test-route",
                    "target": "research",
                    "role": "analyst",
                    "action": "scan",
                    "payload": {"target": "system", "role": "admin", "action": "delete", "symbol": "BTC"},
                }]
            raise asyncio.CancelledError()

    async def run():
        runtime = Runtime()
        runtime.worker_running = True
        captured = []

        async def capture(task_id, payload):
            captured.append((task_id, payload))

        runtime.execute = capture
        with patch("core.runtime.DurableQueue.pending", Queue.pending):
            await runtime._durable_worker()
        assert len(captured) == 1
        task_id, payload = captured[0]
        assert task_id == "test-route"
        assert payload == {"target": "research", "role": "analyst", "action": "scan", "symbol": "BTC"}

    asyncio.run(run())


def test_runtime_without_system_does_not_complete_task():
    async def run():
        runtime = Runtime(system=None)
        with (
            patch("core.runtime.DurableQueue.claim", return_value=True),
            patch("core.runtime.DurableQueue.complete") as complete,
            patch("core.runtime.DurableQueue.fail") as fail,
        ):
            result = await runtime.execute("no-engine", {"target": "research", "action": "scan"})
            assert result["status"] == "failed"
            assert "No execution system attached" in result["error"]
            complete.assert_not_called()
            fail.assert_called_once()

    asyncio.run(run())

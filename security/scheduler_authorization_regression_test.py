import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.scheduler.worker_scheduler import WorkerScheduler


class CountingWorker:
    def __init__(self):
        self.calls = 0

    async def process(self, payload):
        self.calls += 1
        return {"status": "executed"}


async def main():
    scheduler = WorkerScheduler()
    worker = CountingWorker()

    scheduler.register_worker("default", worker)

    # Missing capability must be blocked.
    result = await scheduler.dispatcher.dispatch(
        target="default",
        payload={},
    )

    assert result.get("status") == "blocked"
    assert worker.calls == 0

    # Unknown capability must be blocked.
    result = await scheduler.dispatcher.dispatch(
        target="default",
        payload={
            "capability": "unknown_capability",
        },
    )

    assert result.get("status") == "blocked"
    assert worker.calls == 0

    # Consequential capability without explicit human authorization
    # must be blocked before worker execution.
    result = await scheduler.dispatcher.dispatch(
        target="default",
        payload={
            "capability": "digital_world_operation",
            "action": "execute",
        },
    )

    assert result.get("status") == "blocked"
    assert result.get("authorization", {}).get("requires_authorization") is True
    assert result.get("authorization", {}).get("decision") == "human_required"
    assert worker.calls == 0

    print("=== SCHEDULER AUTHORIZATION REGRESSION ===")
    print("MISSING CAPABILITY: BLOCKED")
    print("UNKNOWN CAPABILITY: BLOCKED")
    print("BLOCKED WORKER EXECUTION: ZERO CALLS")
    print("CONSEQUENTIAL WITHOUT APPROVAL: BLOCKED")
    print("SCHEDULER BYPASS: CLOSED")
    print("STATUS: PASS")


if __name__ == "__main__":
    asyncio.run(main())

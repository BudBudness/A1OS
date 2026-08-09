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

    # Authorized consequential capability must execute.
    result = await scheduler.dispatcher.dispatch(
        target="default",
        payload={
            "capability": "digital_world_operation",
            "action": "execute",
        },
    )

    assert result.get("status") == "executed"
    assert worker.calls == 1

    print("=== SCHEDULER AUTHORIZATION REGRESSION ===")
    print("MISSING CAPABILITY: BLOCKED")
    print("UNKNOWN CAPABILITY: BLOCKED")
    print("BLOCKED WORKER EXECUTION: ZERO CALLS")
    print("AUTHORIZED EXECUTION: PASSED")
    print("SCHEDULER BYPASS: CLOSED")
    print("STATUS: PASS")


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Awaitable

ROOT = Path(os.environ.get(
    "A1OS_ROOT",
    Path(__file__).resolve().parents[2]
))

EVENT_DIR = ROOT / "runtime" / "events"
EVENT_FILE = EVENT_DIR / "events.jsonl"

_subscribers: list[Callable[[dict], Any]] = []
_lock = asyncio.Lock()


def _ensure_store():
    EVENT_DIR.mkdir(parents=True, exist_ok=True)
    EVENT_FILE.touch(exist_ok=True)


async def publish(event: dict):
    _ensure_store()

    record = dict(event)
    record.setdefault("timestamp", time.time())
    record.setdefault("source", "a1os")

    async with _lock:
        with EVENT_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    for subscriber in list(_subscribers):
        try:
            result = subscriber(record)
            if asyncio.iscoroutine(result):
                await result
        except Exception:
            pass

    return record


def subscribe(callback):
    if callback not in _subscribers:
        _subscribers.append(callback)


def event_store():
    _ensure_store()
    return str(EVENT_FILE)


def read_events(limit: int = 100):
    _ensure_store()

    lines = EVENT_FILE.read_text(
        encoding="utf-8"
    ).splitlines()

    result = []

    for line in lines[-max(1, limit):]:
        try:
            result.append(json.loads(line))
        except Exception:
            continue

    return result


class EventBus:
    async def publish(self, event):
        return await publish(event)

    def subscribe(self, callback):
        subscribe(callback)

    def read_events(self, limit=100):
        return read_events(limit)

    def event_store(self):
        return event_store()

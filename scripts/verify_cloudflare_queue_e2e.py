#!/usr/bin/env python3
"""Non-destructive Cloudflare queue acceptance test using a uniquely named smoke task.

Requires A1OS_TASK_QUEUE_URL and A1OS_TASK_QUEUE_TOKEN. Never prints credentials.
The task is claimed and completed by this test, not executed by the production engine.
"""
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
STORE_PATH = REPOSITORY_ROOT / "core" / "persistence" / "cloudflare_tasks.py"
if not STORE_PATH.is_file():
    raise RuntimeError(f"CloudflareTaskStore source file not found: {STORE_PATH}")
SPEC = importlib.util.spec_from_file_location("a1os_cloudflare_tasks", STORE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load CloudflareTaskStore from {STORE_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
CloudflareTaskStore = MODULE.CloudflareTaskStore


def main():
    url = os.getenv("A1OS_TASK_QUEUE_URL", "").strip()
    token = os.getenv("A1OS_TASK_QUEUE_TOKEN", "").strip()
    if not url or not token:
        print("BLOCKED: A1OS_TASK_QUEUE_URL and A1OS_TASK_QUEUE_TOKEN must both be set")
        return 2
    store = CloudflareTaskStore(url=url, token=token)
    task_id = "a1os-acceptance-" + uuid.uuid4().hex
    try:
        created = store.enqueue("staging", "smoke", "noop", {"test": True}, task_id=task_id)
        if created != task_id:
            raise AssertionError("enqueue returned unexpected task ID")
        before = store.get_task(task_id)
        if not before or before.get("status") != "queued":
            raise AssertionError("task was not persisted as queued")
        if not store.claim_task(task_id):
            raise AssertionError("atomic claim failed")
        if store.claim_task(task_id):
            raise AssertionError("duplicate claim succeeded")
        running = store.get_task(task_id)
        if not running or running.get("status") != "running":
            raise AssertionError("running state was not persisted")
        store.complete_task(task_id)
        completed = store.get_task(task_id)
        if not completed or completed.get("status") != "completed":
            raise AssertionError("completed state was not persisted")
        print(json.dumps({"result": "PASS", "task_id": task_id, "checks": ["enqueue", "persist", "claim", "single-claim", "running", "complete", "readback"]}))
        return 0
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

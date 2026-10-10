import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx


class SupabaseTaskStore:
    """Server-side durable task store for Vercel production and workers."""

    def __init__(self) -> None:
        self.url = os.environ.get("SUPABASE_URL", "").rstrip("/")
        self.key = os.environ.get("SUPABASE_SECRET_KEY", "")

    @property
    def configured(self) -> bool:
        return bool(self.url and self.key)

    def _headers(self) -> dict[str, str]:
        if not self.configured:
            raise RuntimeError("Supabase production persistence is not configured")
        return {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }

    def insert_task(self, task_id: str, target: str, role: str, action: str, data: Any) -> None:
        response = httpx.post(
            f"{self.url}/rest/v1/a1os_tasks",
            headers={**self._headers(), "Prefer": "return=minimal"},
            json={"task_id": task_id, "target": target, "role": role, "action": action, "payload": data},
            timeout=10.0,
        )
        response.raise_for_status()

    def enqueue(self, target: str, role: str, action: str, data: Any, task_id: str | None = None) -> str:
        task_id = task_id or str(uuid.uuid4())
        self.insert_task(task_id, target, role, action, data)
        return task_id

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        response = httpx.get(
            f"{self.url}/rest/v1/a1os_tasks",
            headers=self._headers(),
            params={"task_id": f"eq.{task_id}", "select": "*", "limit": "1"},
            timeout=10.0,
        )
        response.raise_for_status()
        rows = response.json()
        return rows[0] if rows else None

    def pending_tasks(self, limit: int = 10) -> list[dict[str, Any]]:
        response = httpx.get(
            f"{self.url}/rest/v1/a1os_tasks",
            headers=self._headers(),
            params={
                "status": "in.(queued,retry)",
                "select": "*",
                "order": "created_at.asc",
                "limit": str(max(1, min(int(limit), 100))),
            },
            timeout=10.0,
        )
        response.raise_for_status()
        rows = response.json()
        if not isinstance(rows, list):
            return []
        now = datetime.now(timezone.utc)
        ready = []
        for row in rows:
            next_attempt = row.get("next_attempt_at")
            if not next_attempt:
                ready.append(row)
                continue
            try:
                scheduled = datetime.fromisoformat(str(next_attempt).replace("Z", "+00:00"))
                if scheduled <= now:
                    ready.append(row)
            except (TypeError, ValueError):
                continue
        return ready

    def claim_task(self, task_id: str) -> bool:
        """Atomically claim a due task through a PostgreSQL function."""
        response = httpx.post(
            f"{self.url}/rest/v1/rpc/a1os_claim_task",
            headers=self._headers(),
            json={"p_task_id": task_id},
            timeout=10.0,
        )
        response.raise_for_status()
        rows = response.json()
        return isinstance(rows, list) and len(rows) == 1

    def recover_stale_tasks(self, stale_after_seconds: int = 300) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=stale_after_seconds)
        response = httpx.get(
            f"{self.url}/rest/v1/a1os_tasks",
            headers=self._headers(),
            params={
                "status": "eq.running",
                "updated_at": f"lt.{cutoff.isoformat()}",
                "select": "task_id,attempts,max_attempts",
                "order": "updated_at.asc",
                "limit": "100",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        rows = response.json()
        if not isinstance(rows, list):
            return 0

        recovered = 0
        now = datetime.now(timezone.utc).isoformat()
        for row in rows:
            task_id = str(row["task_id"])
            attempts = int(row.get("attempts") or 0)
            max_attempts = int(row.get("max_attempts") or 3)
            if attempts >= max_attempts:
                body = {
                    "status": "failed",
                    "error": "Worker lease expired after maximum attempts",
                    "next_attempt_at": None,
                    "updated_at": now,
                }
            else:
                body = {
                    "status": "retry",
                    "error": "Recovered stale running task after worker interruption",
                    "next_attempt_at": now,
                    "updated_at": now,
                }
            patch = httpx.patch(
                f"{self.url}/rest/v1/a1os_tasks",
                headers={**self._headers(), "Prefer": "return=representation"},
                params={"task_id": f"eq.{task_id}", "status": "eq.running"},
                json=body,
                timeout=10.0,
            )
            patch.raise_for_status()
            changed = patch.json()
            if isinstance(changed, list) and changed:
                recovered += 1
        return recovered

    def complete_task(self, task_id: str) -> None:
        completed_at = datetime.now(timezone.utc).isoformat()
        response = httpx.patch(
            f"{self.url}/rest/v1/a1os_tasks",
            headers={**self._headers(), "Prefer": "return=minimal"},
            params={"task_id": f"eq.{task_id}", "status": "eq.running"},
            json={
                "status": "completed",
                "error": None,
                "next_attempt_at": None,
                "completed_at": completed_at,
                "updated_at": completed_at,
            },
            timeout=10.0,
        )
        response.raise_for_status()

    def fail_task(self, task_id: str, error: str) -> None:
        current = self.get_task(task_id)
        if current is None or current.get("status") != "running":
            return
        attempts = int(current.get("attempts") or 0)
        max_attempts = int(current.get("max_attempts") or 3)
        message = str(error).replace("\n", " ")[:1000]
        now = datetime.now(timezone.utc)
        approval_denied = message.startswith("ApprovalDenied:")
        if approval_denied or attempts >= max_attempts:
            body = {
                "status": "failed",
                "error": message,
                "next_attempt_at": None,
                "updated_at": now.isoformat(),
            }
        else:
            delay = 2 ** attempts
            body = {
                "status": "retry",
                "error": message,
                "next_attempt_at": (now + timedelta(seconds=delay)).isoformat(),
                "updated_at": now.isoformat(),
            }
        response = httpx.patch(
            f"{self.url}/rest/v1/a1os_tasks",
            headers={**self._headers(), "Prefer": "return=minimal"},
            params={"task_id": f"eq.{task_id}", "status": "eq.running"},
            json=body,
            timeout=10.0,
        )
        response.raise_for_status()


store = SupabaseTaskStore()

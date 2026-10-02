import os
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx


class SupabaseTaskStore:
    """Server-side durable task store for Vercel production and workers.

    Requires SUPABASE_URL and SUPABASE_SECRET_KEY. The secret key must never
    be exposed to browser code.
    """

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

    def insert_task(
        self,
        task_id: str,
        target: str,
        role: str,
        action: str,
        data: Any,
    ) -> None:
        response = httpx.post(
            f"{self.url}/rest/v1/a1os_tasks",
            headers={**self._headers(), "Prefer": "return=minimal"},
            json={
                "task_id": task_id,
                "target": target,
                "role": role,
                "action": action,
                "payload": data,
            },
            timeout=10.0,
        )
        response.raise_for_status()

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
                "limit": str(limit),
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
            except ValueError:
                ready.append(row)
        return ready

    def claim_task(self, task_id: str) -> bool:
        current = self.get_task(task_id)
        if current is None or current.get("status") not in {"queued", "retry"}:
            return False

        attempts = int(current.get("attempts") or 0) + 1
        response = httpx.patch(
            f"{self.url}/rest/v1/a1os_tasks",
            headers={**self._headers(), "Prefer": "return=representation"},
            params={
                "task_id": f"eq.{task_id}",
                "status": f"eq.{current['status']}",
            },
            json={"status": "running", "attempts": attempts},
            timeout=10.0,
        )
        response.raise_for_status()
        rows = response.json()
        return isinstance(rows, list) and len(rows) == 1

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

        if attempts >= max_attempts:
            body = {
                "status": "failed",
                "error": message,
                "next_attempt_at": None,
            }
        else:
            delay = 2 ** attempts
            body = {
                "status": "retry",
                "error": message,
                "next_attempt_at": (
                    datetime.now(timezone.utc) + timedelta(seconds=delay)
                ).isoformat(),
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

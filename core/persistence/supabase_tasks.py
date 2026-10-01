import os
from typing import Any

import httpx


class SupabaseTaskStore:
    """Server-side durable task store for Vercel production.

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


store = SupabaseTaskStore()

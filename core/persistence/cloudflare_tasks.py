import os
from typing import Any
from urllib.parse import quote

import httpx


class CloudflareTaskStore:
    """HTTP client for the authenticated A1OS Cloudflare D1 task queue Worker."""

    def __init__(self, url: str | None = None, token: str | None = None) -> None:
        self.url = (url if url is not None else os.environ.get("A1OS_TASK_QUEUE_URL", "")).rstrip("/")
        self.token = token if token is not None else os.environ.get("A1OS_TASK_QUEUE_TOKEN", "")

    @property
    def configured(self) -> bool:
        return bool(self.url and self.token)

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        if not self.configured:
            raise RuntimeError("Cloudflare D1 task queue is not configured")
        response = httpx.request(
            method,
            f"{self.url}{path}",
            headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
            timeout=15.0,
            **kwargs,
        )
        response.raise_for_status()
        return response

    def enqueue(self, target: str, role: str, action: str, data: Any, task_id: str | None = None) -> str:
        payload = {"target": target, "role": role, "action": action, "payload": data}
        if task_id:
            payload["task_id"] = task_id
        result = self._request("POST", "/v1/tasks", json=payload).json()
        return str(result["task_id"])

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        response = httpx.get(
            f"{self.url}/v1/tasks/{quote(task_id, safe='')}",
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=15.0,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json().get("data")

    def pending_tasks(self, limit: int = 10) -> list[dict[str, Any]]:
        result = self._request("GET", "/v1/tasks/pending", params={"limit": max(1, min(int(limit), 100))}).json()
        rows = result.get("data", [])
        return rows if isinstance(rows, list) else []

    def claim_task(self, task_id: str) -> bool:
        response = httpx.post(
            f"{self.url}/v1/tasks/{quote(task_id, safe='')}/claim",
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=15.0,
        )
        if response.status_code == 409:
            return False
        response.raise_for_status()
        return bool(response.json().get("claimed"))

    def complete_task(self, task_id: str) -> None:
        self._request("POST", f"/v1/tasks/{quote(task_id, safe='')}/complete")

    def fail_task(self, task_id: str, error: str) -> None:
        self._request("POST", f"/v1/tasks/{quote(task_id, safe='')}/fail", json={"error": str(error)})

    def recover_stale_tasks(self, stale_after_seconds: int = 300) -> int:
        result = self._request(
            "POST",
            "/v1/tasks/recover",
            json={"stale_after_seconds": max(30, min(int(stale_after_seconds), 86400))},
        ).json()
        return int(result.get("recovered", 0))

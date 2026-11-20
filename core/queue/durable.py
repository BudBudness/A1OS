import json
import os
import uuid
from datetime import datetime, timezone

from core.persistence.database import Database


def _cloud_store():
    """Use the Cloudflare D1 queue when configured; never fall back to Supabase."""
    url = os.environ.get("A1OS_TASK_QUEUE_URL", "").strip()
    token = os.environ.get("A1OS_TASK_QUEUE_TOKEN", "").strip()
    if bool(url) != bool(token):
        raise RuntimeError("A1OS_TASK_QUEUE_URL and A1OS_TASK_QUEUE_TOKEN must be configured together")
    if url and token:
        from core.persistence.cloudflare_tasks import CloudflareTaskStore

        return CloudflareTaskStore(url=url, token=token)
    if os.environ.get("VERCEL"):
        raise RuntimeError("Cloudflare D1 task queue is required; legacy Supabase queue fallback is disabled")
    return None


class DurableQueue:
    """Stable queue facade backed by local SQLite or the Cloudflare D1 Worker API."""

    @staticmethod
    def enqueue(target, role, action, data, task_id=None):
        cloud = _cloud_store()
        if cloud is not None:
            return cloud.enqueue(target, role, action, data, task_id=task_id)

        task_id = task_id or str(uuid.uuid4())
        Database.execute(
            """
            INSERT OR REPLACE INTO tasks
            (task_id,target,role,action,payload,status,updated_at)
            VALUES (?,?,?,?,?,'queued',CURRENT_TIMESTAMP)
            """,
            (task_id, target, role, action, json.dumps(data)),
        )
        return task_id

    @staticmethod
    def claim(task_id):
        cloud = _cloud_store()
        if cloud is not None:
            return cloud.claim_task(task_id)

        cur = Database.execute(
            """
            UPDATE tasks
            SET status='running',
                attempts=attempts+1,
                updated_at=CURRENT_TIMESTAMP
            WHERE task_id=?
              AND (
                    status='queued'
                    OR (
                        status='retry'
                        AND (
                            next_attempt_at IS NULL
                            OR datetime(next_attempt_at) <= CURRENT_TIMESTAMP
                        )
                    )
                  )
            """,
            (task_id,),
        )
        return cur.rowcount == 1

    @staticmethod
    def complete(task_id):
        cloud = _cloud_store()
        if cloud is not None:
            return cloud.complete_task(task_id)

        Database.execute(
            """
            UPDATE tasks
            SET status='completed',
                completed_at=CURRENT_TIMESTAMP,
                error=NULL,
                next_attempt_at=NULL,
                updated_at=CURRENT_TIMESTAMP
            WHERE task_id=?
            """,
            (task_id,),
        )

    @staticmethod
    def fail(task_id, error):
        cloud = _cloud_store()
        if cloud is not None:
            message = str(error)
            if error.__class__.__name__ == "ApprovalDenied":
                message = f"ApprovalDenied: {message}"
            return cloud.fail_task(task_id, message)

        # Approval denials are terminal: retrying cannot manufacture authorization.
        if error.__class__.__name__ == "ApprovalDenied":
            Database.execute(
                """
                UPDATE tasks
                SET status='failed',
                    error=?,
                    next_attempt_at=NULL,
                    updated_at=CURRENT_TIMESTAMP
                WHERE task_id=?
                """,
                (str(error), task_id),
            )
            return

        row = Database.fetchone(
            "SELECT attempts, max_attempts FROM tasks WHERE task_id=?",
            (task_id,),
        )
        if not row:
            return

        attempts = row["attempts"]
        max_attempts = row["max_attempts"]
        if attempts >= max_attempts:
            Database.execute(
                """
                UPDATE tasks
                SET status='failed',
                    error=?,
                    next_attempt_at=NULL,
                    updated_at=CURRENT_TIMESTAMP
                WHERE task_id=?
                """,
                (str(error), task_id),
            )
            return

        delay_seconds = 2 ** attempts
        Database.execute(
            f"""
            UPDATE tasks
            SET status='retry',
                error=?,
                next_attempt_at=datetime('now', '+{delay_seconds} seconds'),
                updated_at=CURRENT_TIMESTAMP
            WHERE task_id=?
            """,
            (str(error), task_id),
        )

    @staticmethod
    def recover_running(stale_after_seconds=300):
        stale_after_seconds = max(0, int(stale_after_seconds))
        cloud = _cloud_store()
        if cloud is not None:
            return cloud.recover_stale_tasks(stale_after_seconds=stale_after_seconds)

        cur = Database.execute(
            """
            UPDATE tasks
            SET status='retry',
                updated_at=CURRENT_TIMESTAMP,
                error='Recovered after process interruption',
                next_attempt_at=NULL
            WHERE status='running'
              AND datetime(updated_at) < datetime('now', ? || ' seconds')
            """,
            ("-" + str(stale_after_seconds),),
        )
        return cur.rowcount

    @staticmethod
    def get(task_id):
        cloud = _cloud_store()
        if cloud is not None:
            return cloud.get_task(task_id)
        return Database.fetchone("SELECT * FROM tasks WHERE task_id=?", (task_id,))

    @staticmethod
    def pending(limit=10):
        cloud = _cloud_store()
        if cloud is not None:
            return cloud.pending_tasks(limit=limit)
        return Database.fetchall(
            """
            SELECT *
            FROM tasks
            WHERE status IN ('queued', 'retry')
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (limit,),
        )

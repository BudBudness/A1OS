import json
import uuid
from datetime import datetime, timezone
from core.persistence.database import Database

class DurableQueue:
    @staticmethod
    def enqueue(target, role, action, data, task_id=None):
        task_id = task_id or str(uuid.uuid4())
        Database.execute(
            """
            INSERT OR REPLACE INTO tasks
            (task_id,target,role,action,payload,status,updated_at)
            VALUES (?,?,?,?,?,'queued',CURRENT_TIMESTAMP)
            """,
            (task_id, target, role, action, json.dumps(data))
        )
        return task_id

    @staticmethod
    def claim(task_id):
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
            (task_id,)
        )
        return cur.rowcount == 1

    @staticmethod
    def complete(task_id):
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
            (task_id,)
        )

    @staticmethod
    def fail(task_id, error):
        row = Database.fetchone(
            """
            SELECT attempts, max_attempts
            FROM tasks
            WHERE task_id=?
            """,
            (task_id,)
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
                (str(error), task_id)
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
            (str(error), task_id)
        )

    @staticmethod
    def recover_running():
        """
        Recover tasks stranded in running state after
        an interrupted process.

        Running tasks become retryable. Their retry schedule
        is reset so the durable worker can reclaim them.
        """
        cur = Database.execute(
            """
            UPDATE tasks
            SET status='retry',
                updated_at=CURRENT_TIMESTAMP,
                error='Recovered after process interruption',
                next_attempt_at=NULL
            WHERE status='running'
            """
        )
        return cur.rowcount

    @staticmethod
    def get(task_id):
        return Database.fetchone(
            "SELECT * FROM tasks WHERE task_id=?",
            (task_id,)
        )

    @staticmethod
    def pending(limit=10):
        return Database.fetchall(
            """
            SELECT *
            FROM tasks
            WHERE status IN ('queued', 'retry')
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (limit,)
        )

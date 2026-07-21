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
        Database.execute(
            """
            UPDATE tasks
            SET status='running',
                attempts=attempts+1,
                updated_at=CURRENT_TIMESTAMP
            WHERE task_id=? AND status IN ('queued','retry')
            """,
            (task_id,)
        )

    @staticmethod
    def complete(task_id):
        Database.execute(
            """
            UPDATE tasks
            SET status='completed',
                completed_at=CURRENT_TIMESTAMP,
                error=NULL,
                updated_at=CURRENT_TIMESTAMP
            WHERE task_id=?
            """,
            (task_id,)
        )

    @staticmethod
    def fail(task_id, error):
        Database.execute(
            """
            UPDATE tasks
            SET status='failed',
                error=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE task_id=?
            """,
            (str(error), task_id)
        )

    @staticmethod
    def recover_running():
        """
        Recover tasks stranded in running state after an interrupted process.
        They are made retryable for future worker execution.
        """
        cur = Database.execute(
            """
            UPDATE tasks
            SET status='retry',
                updated_at=CURRENT_TIMESTAMP,
                error='Recovered after process interruption'
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

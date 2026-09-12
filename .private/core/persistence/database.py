import sqlite3
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "a1os.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

class Database:
    _local = threading.local()

    @classmethod
    def connection(cls):
        conn = getattr(cls._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA busy_timeout=5000")

        # Canonical durable execution queue schema.
        # Created at the persistence boundary so every real Runtime/worker
        # using DurableQueue receives the same task store.
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            target TEXT NOT NULL,
            role TEXT NOT NULL,
            action TEXT NOT NULL,
            payload TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'queued',
            attempts INTEGER NOT NULL DEFAULT 0,
            max_attempts INTEGER NOT NULL DEFAULT 3,
            error TEXT,
            next_attempt_at TEXT,
            completed_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_tasks_pending
        ON tasks(status, next_attempt_at, created_at);

        CREATE INDEX IF NOT EXISTS idx_tasks_target
        ON tasks(target);
        """)
        conn.commit()

        cls._local.conn = conn
        return conn

    @classmethod
    def close(cls):
        """Close and clear the current thread-local database connection."""
        conn = getattr(cls._local, "conn", None)
        if conn is not None:
            try:
                conn.close()
            finally:
                try:
                    del cls._local.conn
                except AttributeError:
                    pass

    @classmethod
    def execute(cls, sql, params=()):
        conn = cls.connection()
        cur = conn.execute(sql, params)
        conn.commit()
        return cur

    @classmethod
    def fetchone(cls, sql, params=()):
        return cls.connection().execute(sql, params).fetchone()

    @classmethod
    def fetchall(cls, sql, params=()):
        return cls.connection().execute(sql, params).fetchall()

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
            cls._local.conn = conn
        return conn

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

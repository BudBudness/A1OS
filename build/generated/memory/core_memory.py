import sqlite3
import os
import threading
from pathlib import Path

class SovereignMemoryEngine:
    def __init__(self, db_path=None):
        if db_path is None:
            db_dir = Path(os.path.expanduser("~")) / "A1OS/data"
            db_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = db_dir / "a1os_state.db"
        else:
            self.db_path = Path(db_path)
        self._local = threading.local()
        self._init_db()

    def _get_connection(self):
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(str(self.db_path), timeout=30.0)
            self._local.conn.execute("PRAGMA journal_mode=WAL;")
            self._local.conn.execute("PRAGMA synchronous=NORMAL;")
        return self._local.conn

    def _init_db(self):
        conn = self._get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS system_state (
                key TEXT PRIMARY KEY, value TEXT, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

    def store_state(self, key, value):
        conn = self._get_connection()
        conn.execute("INSERT OR REPLACE INTO system_state (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()

    def fetch_state(self, key):
        cursor = self._get_connection().cursor()
        cursor.execute("SELECT value FROM system_state WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None
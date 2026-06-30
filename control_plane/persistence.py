import sqlite3
import os
import logging

logger = logging.getLogger("A1OS-Persistence")

class PersistenceEngine:
    def __init__(self, db_path: str = "a1os_state.db"):
        self.db_path = db_path
        self._init_schema()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_trail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    module TEXT,
                    action TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS kv_store (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()
        logger.info(f"[DB] 🗄️ Persistent SQLite Engine initialized at: {self.db_path}")

    def log_audit(self, module: str, action: str):
        with self._get_connection() as conn:
            conn.execute("INSERT INTO audit_trail (module, action) VALUES (?, ?)", (module, action))
            conn.commit()

    def set_kv(self, key: str, value: str):
        with self._get_connection() as conn:
            conn.execute("INSERT OR REPLACE INTO kv_store (key, value) VALUES (?, ?)", (key, value))
            conn.commit()

    def get_kv(self, key: str) -> str:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM kv_store WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else ""

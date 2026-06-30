import sqlite3
import logging

class PersistenceManager:
    def __init__(self, db_path="a1os_state.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("A1OS-Persistence")
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS permissions (
                    plugin_name TEXT,
                    scope TEXT,
                    PRIMARY KEY (plugin_name, scope)
                )
            """)

    def save_grant(self, plugin_name, scope):
        with self._connect() as conn:
            conn.execute("INSERT OR REPLACE INTO permissions VALUES (?, ?)", (plugin_name, scope))
            self.logger.info(f"[DB] Persisted grant: {plugin_name} -> {scope}")

    def load_grants(self):
        with self._connect() as conn:
            return conn.execute("SELECT plugin_name, scope FROM permissions").fetchall()

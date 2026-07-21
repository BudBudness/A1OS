import sqlite3
import json
import uuid
from typing import Dict, Any, Optional

class KnowledgeBase:
    def __init__(self, db_path: str = "a1os_state.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    attributes TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_kv (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def add_entity(self, entity_type: str, attributes: Dict[str, Any]) -> str:
        entity_id = uuid.uuid4().hex
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO entities (id, entity_type, attributes) VALUES (?, ?, ?)",
                (entity_id, entity_type, json.dumps(attributes))
            )
            conn.commit()
        return entity_id

    def set_meta(self, key: str, value: Any):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO system_kv (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (key, json.dumps(value))
            )
            conn.commit()

    def get_meta(self, key: str, default: Any = None) -> Any:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM system_kv WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
        return default

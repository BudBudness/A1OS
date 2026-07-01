import sqlite3
from pathlib import Path

class LongTermMemoryStore:
    def __init__(self, db_path=":memory:"):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path)
        self._init_table()

    def _init_table(self):
        with self._conn:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS long_term_knowledge (
                    entity_id TEXT PRIMARY KEY,
                    content TEXT,
                    category TEXT,
                    created_at REAL
                )
            """)

    def insert_knowledge(self, entity_id, content, category, timestamp):
        with self._conn:
            self._conn.execute(
                "INSERT OR REPLACE INTO long_term_knowledge VALUES (?, ?, ?, ?)",
                (entity_id, content, category, timestamp)
            )
        print(f"[KNOWLEDGE-STORE] Stored long-term entity record: {entity_id}")

    def fetch_knowledge(self, entity_id):
        cursor = self._conn.cursor()
        cursor.execute("SELECT content, category FROM long_term_knowledge WHERE entity_id = ?", (entity_id,))
        row = cursor.fetchone()
        return {"content": row[0], "category": row[1]} if row else None
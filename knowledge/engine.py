import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any

class KnowledgeEngine:
    def __init__(self, db_path: str = "data/a1os.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS knowledge (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    metadata TEXT,
                    created TEXT,
                    updated TEXT
                )
            ''')

    def set(self, key: str, value: Any, metadata: Dict = None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO knowledge (key, value, metadata, created, updated) VALUES (?, ?, ?, ?, ?)",
                (key, json.dumps(value), json.dumps(metadata or {}), datetime.now().isoformat(), datetime.now().isoformat())
            )
            conn.commit()

    def get(self, key: str) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT * FROM knowledge WHERE key = ?", (key,)).fetchone()
            if not row:
                return None
            return {"key": row[0], "value": json.loads(row[1]), "metadata": json.loads(row[2]), "created": row[3], "updated": row[4]}

    def get_all(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM knowledge").fetchall()
            return [{"key": r[0], "value": json.loads(r[1]), "metadata": json.loads(r[2]), "created": r[3], "updated": r[4]} for r in rows]

    def delete(self, key: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM knowledge WHERE key = ?", (key,))
            conn.commit()

    def search(self, query: str) -> List[Dict]:
        q = query.lower()
        return [k for k in self.get_all() if q in k["key"].lower() or q in str(k["value"]).lower()]

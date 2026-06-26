import sqlite3
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any

class MemoryEngine:
    def __init__(self, db_path: str = "data/a1os.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS memory (
                    id TEXT PRIMARY KEY,
                    text TEXT,
                    tags TEXT,
                    created TEXT
                )
            ''')

    def store(self, text: str, tags: List[str] = None) -> Dict[str, Any]:
        doc_id = hashlib.md5(text.encode()).hexdigest()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO memory (id, text, tags, created) VALUES (?, ?, ?, ?)",
                (doc_id, text, json.dumps(tags or []), datetime.now().isoformat())
            )
            conn.commit()
        return {"id": doc_id, "text": text, "tags": tags or [], "created": datetime.now().isoformat()}

    def get_all(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM memory").fetchall()
            return [{"id": r[0], "text": r[1], "tags": json.loads(r[2]), "created": r[3]} for r in rows]

    def search(self, query: str) -> List[Dict[str, Any]]:
        q = query.lower()
        return [m for m in self.get_all() if q in m["text"].lower()]

    def stats(self) -> Dict[str, Any]:
        items = self.get_all()
        return {"total": len(items), "tags": list(set(tag for item in items for tag in item["tags"]))}

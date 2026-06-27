import sqlite3, json, hashlib
from datetime import datetime

class MemoryEngine:
    def __init__(self, db_path='data/a1os.db'):
        self.db_path = db_path
    def store(self, content, mem_type='long_term', metadata=None):
        doc_id = hashlib.md5(content.encode()).hexdigest()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO memory (id, content, type, metadata, created) VALUES (?, ?, ?, ?, ?)",
                         (doc_id, content, mem_type, json.dumps(metadata or {}), datetime.now().isoformat()))
            conn.commit()
        return {"id": doc_id, "content": content, "type": mem_type}
    def search(self, query):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM memory WHERE content LIKE ?", (f'%{query}%',)).fetchall()
            return [{"id": r[0], "content": r[1], "type": r[2], "created": r[4]} for r in rows]
    def stats(self):
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM memory").fetchone()[0] or 0
            long_term = conn.execute("SELECT COUNT(*) FROM memory WHERE type='long_term'").fetchone()[0] or 0
            working = conn.execute("SELECT COUNT(*) FROM memory WHERE type='working'").fetchone()[0] or 0
            return {"total": total, "long_term": long_term, "working": working}

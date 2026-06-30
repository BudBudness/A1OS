
import sqlite3, json, hashlib
from datetime import datetime
DB_PATH = "data/memory.db"
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, content TEXT, type TEXT, metadata TEXT, created TEXT)")
def store(content, mem_type="long_term"):
    doc_id = hashlib.md5(content.encode()).hexdigest()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR REPLACE INTO memory (id, content, type, metadata, created) VALUES (?, ?, ?, ?, ?)",
                     (doc_id, content, mem_type, "{{}}", datetime.now().isoformat()))
        conn.commit()
    return {"id": doc_id}
init_db()
print("✅ Memory engine initialized")

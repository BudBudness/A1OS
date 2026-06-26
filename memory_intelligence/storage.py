from typing import List, Dict, Optional, Any
import json
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from .models import MemoryItem, MemoryStats

class Storage:
    def __init__(self, db_path: str = 'data/memory.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS memory_items (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    type TEXT,
                    timestamp TEXT,
                    metadata TEXT,
                    importance REAL,
                    access_count INTEGER,
                    last_accessed TEXT,
                    expires_at TEXT
                );
                CREATE TABLE IF NOT EXISTS knowledge_graph (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT,
                    target TEXT,
                    relation TEXT,
                    metadata TEXT,
                    created TEXT
                );
                CREATE TABLE IF NOT EXISTS memory_stats (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated TEXT
                );
            ''')

    def save(self, item: MemoryItem):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO memory_items
                (id, content, type, timestamp, metadata, importance, access_count, last_accessed, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.id, item.content, item.type, item.timestamp.isoformat(),
                json.dumps(item.metadata), item.importance, item.access_count,
                item.last_accessed.isoformat() if item.last_accessed else None,
                item.expires_at.isoformat() if item.expires_at else None
            ))
            conn.commit()

    def get(self, item_id: str) -> Optional[MemoryItem]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute('SELECT * FROM memory_items WHERE id = ?', (item_id,)).fetchone()
            if not row:
                return None
            return MemoryItem(
                id=row[0], content=row[1], type=row[2],
                timestamp=datetime.fromisoformat(row[3]),
                metadata=json.loads(row[4]),
                importance=row[5], access_count=row[6],
                last_accessed=datetime.fromisoformat(row[7]) if row[7] else None,
                expires_at=datetime.fromisoformat(row[8]) if row[8] else None
            )

    def get_all(self, memory_type: Optional[str] = None) -> List[MemoryItem]:
        with sqlite3.connect(self.db_path) as conn:
            query = 'SELECT * FROM memory_items'
            params = []
            if memory_type:
                query += ' WHERE type = ?'
                params.append(memory_type)
            rows = conn.execute(query, params).fetchall()
            return [
                MemoryItem(
                    id=r[0], content=r[1], type=r[2],
                    timestamp=datetime.fromisoformat(r[3]),
                    metadata=json.loads(r[4]),
                    importance=r[5], access_count=r[6],
                    last_accessed=datetime.fromisoformat(r[7]) if r[7] else None,
                    expires_at=datetime.fromisoformat(r[8]) if r[8] else None
                ) for r in rows
            ]

    def delete(self, item_id: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM memory_items WHERE id = ?', (item_id,))
            conn.commit()

    def get_stats(self) -> MemoryStats:
        with sqlite3.connect(self.db_path) as conn:
            stats = MemoryStats()
            stats.total = conn.execute('SELECT COUNT(*) FROM memory_items').fetchone()[0]
            stats.working = conn.execute("SELECT COUNT(*) FROM memory_items WHERE type = 'working'").fetchone()[0]
            stats.episodic = conn.execute("SELECT COUNT(*) FROM memory_items WHERE type = 'episodic'").fetchone()[0]
            stats.long_term = conn.execute("SELECT COUNT(*) FROM memory_items WHERE type = 'long_term'").fetchone()[0]
            stats.vector = conn.execute("SELECT COUNT(*) FROM memory_items WHERE type = 'vector'").fetchone()[0]
            stats.graph_nodes = conn.execute('SELECT COUNT(*) FROM knowledge_graph').fetchone()[0]
            # Simple avg importance
            avg = conn.execute('SELECT AVG(importance) FROM memory_items').fetchone()[0]
            stats.avg_importance = avg or 0.0
            return stats

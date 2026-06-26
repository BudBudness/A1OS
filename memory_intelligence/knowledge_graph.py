from typing import List, Dict, Optional, Any
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

class KnowledgeGraph:
    def __init__(self, db_path: str = 'data/memory.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS knowledge_graph (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT,
                    target TEXT,
                    relation TEXT,
                    metadata TEXT,
                    created TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_kg_source ON knowledge_graph(source);
                CREATE INDEX IF NOT EXISTS idx_kg_target ON knowledge_graph(target);
            ''')

    def add_relation(self, source: str, target: str, relation: str, metadata: dict = None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO knowledge_graph (source, target, relation, metadata, created)
                VALUES (?, ?, ?, ?, ?)
            ''', (source, target, relation, json.dumps(metadata or {}), datetime.now().isoformat()))
            conn.commit()

    def get_relations(self, source: str, relation: Optional[str] = None) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            query = 'SELECT * FROM knowledge_graph WHERE source = ?'
            params = [source]
            if relation:
                query += ' AND relation = ?'
                params.append(relation)
            rows = conn.execute(query, params).fetchall()
            return [
                {
                    'id': r[0], 'source': r[1], 'target': r[2],
                    'relation': r[3], 'metadata': json.loads(r[4]),
                    'created': r[5]
                } for r in rows
            ]

    def get_targets(self, source: str, relation: str) -> List[str]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                'SELECT target FROM knowledge_graph WHERE source = ? AND relation = ?',
                (source, relation)
            ).fetchall()
            return [r[0] for r in rows]

    def get_sources(self, target: str, relation: str) -> List[str]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                'SELECT source FROM knowledge_graph WHERE target = ? AND relation = ?',
                (target, relation)
            ).fetchall()
            return [r[0] for r in rows]

    def get_all_relations(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute('SELECT * FROM knowledge_graph').fetchall()
            return [
                {
                    'id': r[0], 'source': r[1], 'target': r[2],
                    'relation': r[3], 'metadata': json.loads(r[4]),
                    'created': r[5]
                } for r in rows
            ]

    def get_stats(self) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            nodes = conn.execute(
                'SELECT COUNT(DISTINCT source) FROM knowledge_graph'
            ).fetchone()[0] + conn.execute(
                'SELECT COUNT(DISTINCT target) FROM knowledge_graph'
            ).fetchone()[0]
            edges = conn.execute('SELECT COUNT(*) FROM knowledge_graph').fetchone()[0]
            return {'nodes': nodes, 'edges': edges}

from typing import List, Dict, Any
import json
import sqlite3
from datetime import datetime

class WorkflowEngine:
    def __init__(self, db_path: str = "data/a1os.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS workflows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    steps TEXT,
                    status TEXT,
                    created TEXT,
                    completed TEXT
                )
            ''')

    def create(self, name: str, steps: List[Dict]) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT INTO workflows (name, steps, status, created) VALUES (?, ?, ?, ?)",
                (name, json.dumps(steps), "pending", datetime.now().isoformat())
            )
            conn.commit()
            return {"id": cur.lastrowid, "name": name, "status": "pending"}

    def get_all(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM workflows").fetchall()
            return [{"id": r[0], "name": r[1], "steps": json.loads(r[2]), "status": r[3], "created": r[4], "completed": r[5]} for r in rows]

    def execute(self, workflow_id: int) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE workflows SET status = 'running', completed = ? WHERE id = ?", (datetime.now().isoformat(), workflow_id))
            conn.commit()
        # Simulate execution
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE workflows SET status = 'completed' WHERE id = ?", (workflow_id,))
            conn.commit()
        return {"ok": True, "id": workflow_id}

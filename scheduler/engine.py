import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any
import threading
import time

class SchedulerEngine:
    def __init__(self, db_path: str = "data/a1os.db"):
        self.db_path = db_path
        self._init_db()
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    schedule TEXT,
                    action TEXT,
                    metadata TEXT,
                    status TEXT,
                    created TEXT,
                    last_run TEXT,
                    next_run TEXT
                )
            ''')

    def add(self, name: str, schedule: str, action: str, metadata: Dict = None) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT INTO scheduled_tasks (name, schedule, action, metadata, status, created, last_run, next_run) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (name, schedule, action, json.dumps(metadata or {}), "pending", datetime.now().isoformat(), None, datetime.now().isoformat())
            )
            conn.commit()
            return {"id": cur.lastrowid, "name": name, "schedule": schedule, "action": action, "status": "pending"}

    def get_all(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM scheduled_tasks").fetchall()
            return [{"id": r[0], "name": r[1], "schedule": r[2], "action": r[3], "metadata": json.loads(r[4] or "{}"), "status": r[5], "created": r[6], "last_run": r[7], "next_run": r[8]} for r in rows]

    def run_task(self, task_id: int) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE scheduled_tasks SET status = 'running', last_run = ? WHERE id = ?", (datetime.now().isoformat(), task_id))
            conn.commit()
        # Simulate task execution
        time.sleep(1)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE scheduled_tasks SET status = 'completed' WHERE id = ?", (task_id,))
            conn.commit()
        return {"ok": True, "id": task_id}

    def _run(self):
        while self.running:
            time.sleep(10)
            # Check for pending tasks and run them
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute("SELECT * FROM scheduled_tasks WHERE status = 'pending' LIMIT 1").fetchall()
                if rows:
                    self.run_task(rows[0][0])

    def stop(self):
        self.running = False

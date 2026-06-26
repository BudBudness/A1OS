import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any
import threading
import time

class AgentEngine:
    def __init__(self, db_path: str = "data/a1os.db"):
        self.db_path = db_path
        self._init_db()
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    type TEXT,
                    status TEXT,
                    metadata TEXT,
                    created TEXT,
                    last_active TEXT
                )
            ''')

    def create(self, name: str, agent_type: str = "general", metadata: Dict = None) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT INTO agents (name, type, status, metadata, created, last_active) VALUES (?, ?, ?, ?, ?, ?)",
                (name, agent_type, "idle", json.dumps(metadata or {}), datetime.now().isoformat(), datetime.now().isoformat())
            )
            conn.commit()
            return {"id": cur.lastrowid, "name": name, "type": agent_type, "status": "idle"}

    def get_all(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM agents").fetchall()
            return [{"id": r[0], "name": r[1], "type": r[2], "status": r[3], "metadata": json.loads(r[4] or "{}"), "created": r[5], "last_active": r[6]} for r in rows]

    def update_status(self, agent_id: int, status: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE agents SET status = ?, last_active = ? WHERE id = ?", (status, datetime.now().isoformat(), agent_id))
            conn.commit()

    def _run(self):
        while self.running:
            time.sleep(5)
            # Simulate agent activity
            agents = self.get_all()
            for agent in agents:
                if agent["status"] == "idle":
                    self.update_status(agent["id"], "active")
                    time.sleep(1)
                    self.update_status(agent["id"], "idle")

    def stop(self):
        self.running = False

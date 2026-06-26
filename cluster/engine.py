import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any
import threading
import time

class ClusterEngine:
    def __init__(self, db_path: str = "data/a1os.db"):
        self.db_path = db_path
        self._init_db()
        self.leader = None
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cluster_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    address TEXT,
                    status TEXT,
                    metadata TEXT,
                    joined TEXT,
                    last_heartbeat TEXT
                )
            ''')

    def add_node(self, address: str, metadata: Dict = None) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT INTO cluster_nodes (address, status, metadata, joined, last_heartbeat) VALUES (?, ?, ?, ?, ?)",
                (address, "active", json.dumps(metadata or {}), datetime.now().isoformat(), datetime.now().isoformat())
            )
            conn.commit()
            if not self.leader:
                self.leader = cur.lastrowid
            return {"id": cur.lastrowid, "address": address, "status": "active"}

    def get_nodes(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM cluster_nodes").fetchall()
            return [{"id": r[0], "address": r[1], "status": r[2], "metadata": json.loads(r[3]), "joined": r[4], "last_heartbeat": r[5]} for r in rows]

    def heartbeat(self, node_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE cluster_nodes SET last_heartbeat = ? WHERE id = ?", (datetime.now().isoformat(), node_id))
            conn.commit()

    def elect_leader(self):
        nodes = self.get_nodes()
        if nodes:
            self.leader = nodes[0]["id"]

    def _run(self):
        while self.running:
            time.sleep(10)
            self.elect_leader()

    def stop(self):
        self.running = False

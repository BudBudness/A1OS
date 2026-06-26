import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any
import threading
import time

class ConsensusEngine:
    def __init__(self, db_path: str = "data/a1os.db"):
        self.db_path = db_path
        self._init_db()
        self.term = 0
        self.votes = {}
        self.running = True

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS consensus_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    term INTEGER,
                    proposal TEXT,
                    status TEXT,
                    metadata TEXT,
                    timestamp TEXT
                )
            ''')

    def propose(self, proposal: str, metadata: Dict = None) -> Dict:
        self.term += 1
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT INTO consensus_log (term, proposal, status, metadata, timestamp) VALUES (?, ?, ?, ?, ?)",
                (self.term, proposal, "proposed", json.dumps(metadata or {}), datetime.now().isoformat())
            )
            conn.commit()
            return {"id": cur.lastrowid, "term": self.term, "proposal": proposal, "status": "proposed"}

    def get_log(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM consensus_log ORDER BY term DESC").fetchall()
            return [{"id": r[0], "term": r[1], "proposal": r[2], "status": r[3], "metadata": json.loads(r[4]), "timestamp": r[5]} for r in rows]

    def vote(self, log_id: int, vote: bool):
        with sqlite3.connect(self.db_path) as conn:
            status = "committed" if vote else "rejected"
            conn.execute("UPDATE consensus_log SET status = ? WHERE id = ?", (status, log_id))
            conn.commit()

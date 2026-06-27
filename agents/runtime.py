import sqlite3, json, threading, time
from datetime import datetime

class AgentRuntime:
    def __init__(self, db_path='data/a1os.db'):
        self.db_path = db_path
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()
    def _loop(self):
        while self.running:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    rows = conn.execute("SELECT * FROM agents WHERE status = 'idle' LIMIT 1").fetchall()
                    for agent in rows:
                        conn.execute("UPDATE agents SET status = 'working', last_active = ? WHERE id = ?",
                                     (datetime.now().isoformat(), agent['id']))
                        conn.commit()
                time.sleep(10)
            except:
                time.sleep(10)

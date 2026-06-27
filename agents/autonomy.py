import threading, time, json, sqlite3
from datetime import datetime

class AgentAutonomy:
    def __init__(self):
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        while self.running:
            try:
                conn = sqlite3.connect('data/a1os.db')
                conn.row_factory = sqlite3.Row
                agents = conn.execute("SELECT * FROM agents").fetchall()
                for agent in agents:
                    agent_id = agent["id"]
                    name = agent["name"]
                    status = agent["status"]
                    if status == "idle":
                        # Set a goal
                        goal = f"Process {name} tasks"
                        conn.execute("INSERT OR REPLACE INTO agent_goals (agent_id, description, status, created) VALUES (?, ?, ?, ?)",
                                     (agent_id, goal, "pending", datetime.now().isoformat()))
                        conn.execute("UPDATE agents SET status = 'working', last_active = ? WHERE id = ?",
                                     (datetime.now().isoformat(), agent_id))
                        conn.commit()
                        # Log it
                        conn.execute("INSERT INTO agent_logs (agent_id, log, created) VALUES (?, ?, ?)",
                                     (agent_id, f"Started working on: {goal}", datetime.now().isoformat()))
                        conn.commit()
                conn.close()
                time.sleep(30)
            except Exception as e:
                print(f"Agent error: {e}")
                time.sleep(10)

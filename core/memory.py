import sqlite3
import json

class MemoryManager:
    def __init__(self, db_path="memory.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("CREATE TABLE IF NOT EXISTS episodic (id INTEGER PRIMARY KEY, event_type TEXT, context TEXT, outcome TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
    
    def record_decision(self, event, context, outcome):
        self.conn.execute("INSERT INTO episodic (event_type, context, outcome) VALUES (?, ?, ?)", 
                         (event, json.dumps(context), outcome))
        self.conn.commit()

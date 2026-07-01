import sqlite3
import json

class DatabaseManager:
    def __init__(self, db_path="~/A1OS/audit.db"):
        self.conn = sqlite3.connect(db_path.replace("~", "/data/data/com.termux/files/home"))
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks 
            (task_id TEXT PRIMARY KEY, data TEXT, status TEXT)''')
        self.conn.commit()

    def save_task(self, task):
        self.cursor.execute("REPLACE INTO tasks VALUES (?,?,?)", 
                            (task.task_id, json.dumps(task.__dict__), task.status))
        self.conn.commit()

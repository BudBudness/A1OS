from workflow.engine import WorkflowEngine
import sqlite3

class Dashboard:
    @staticmethod
    def get_system_metrics():
        conn = sqlite3.connect("/data/data/com.termux/files/home/A1OS/audit.db")
        tasks = conn.execute("SELECT data FROM tasks").fetchall()
        conn.close()
        return len(tasks), [len(task[0]) for task in tasks]

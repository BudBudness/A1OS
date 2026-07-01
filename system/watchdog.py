import sqlite3
class Watchdog:
    @staticmethod
    def check_budget(limit):
        with sqlite3.connect("/data/data/com.termux/files/home/A1OS/audit.db") as conn:
            spent = conn.execute("SELECT SUM(budget) FROM tasks").fetchone()[0] or 0
        return spent < limit

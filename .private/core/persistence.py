import sqlite3

class Persistence:
    def __init__(self, db_path="data/a1os.db"):
        self.conn = sqlite3.connect(db_path)
        self.setup()

    def setup(self):
        self.conn.execute("CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT)")
        self.conn.commit()

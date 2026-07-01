import sqlite3
import os

db_path = os.path.expanduser("~/A1OS/data/audit.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT * FROM audit")
rows = cursor.fetchall()

print(f"Audit Log Records: {len(rows)}")
for row in rows:
    print(row)

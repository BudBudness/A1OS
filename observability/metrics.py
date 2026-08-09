import sqlite3
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "a1os.db"

def record_metric(name: str, value: float = 1.0, labels: str = ""):
    with sqlite3.connect(DB) as conn:
        conn.execute(
            """
            INSERT INTO metrics
            (name, value, labels, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (name, value, labels, int(time.time())),
        )
        conn.commit()

def increment(name: str, labels: str = ""):
    record_metric(name, 1.0, labels)

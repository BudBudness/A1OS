import sqlite3
import time

_DB = "data/a1os.db"

def increment(name, value=1, labels=None):
    labels = labels or {}
    try:
        con = sqlite3.connect(_DB)
        con.execute(
            """
            INSERT INTO metrics (name, value, labels, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                str(name),
                float(value),
                str(labels),
                time.time(),
            ),
        )
        con.commit()
        con.close()
    except Exception:
        pass

    return {
        "name": name,
        "value": value,
        "labels": labels,
    }

__all__ = ["increment"]

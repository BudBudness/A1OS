import os
import sqlite3
import time

def health_snapshot():
    root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../..")
    )

    database = os.path.join(root, "data", "a1os.db")

    snapshot = {
        "status": "healthy",
        "runtime": root,
        "timestamp": time.time(),
        "database": {
            "path": database,
            "exists": os.path.exists(database),
            "integrity": "unknown",
        },
    }

    if os.path.exists(database):
        try:
            con = sqlite3.connect(database)
            integrity = con.execute(
                "PRAGMA integrity_check"
            ).fetchone()[0]
            con.close()
            snapshot["database"]["integrity"] = integrity
        except Exception as exc:
            snapshot["database"]["integrity"] = f"error: {exc}"

    return snapshot

__all__ = ["health_snapshot"]

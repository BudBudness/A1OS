import sqlite3
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "a1os.db"

def health_snapshot():
    result = {
        "runtime": "online",
        "database": "unknown",
        "database_integrity": "unknown",
        "timestamp": int(time.time()),
    }

    try:
        with sqlite3.connect(DB) as conn:
            result["database"] = "online"
            result["database_integrity"] = conn.execute(
                "PRAGMA integrity_check"
            ).fetchone()[0]
    except Exception as exc:
        result["database"] = "offline"
        result["error"] = str(exc)

    return result

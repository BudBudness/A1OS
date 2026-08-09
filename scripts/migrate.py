import hashlib
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "a1os.db"
MIGRATIONS = ROOT / "migrations"

conn = sqlite3.connect(DB)
conn.execute("""
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
""")

for path in sorted(MIGRATIONS.glob("*.sql")):
    version = path.name
    exists = conn.execute(
        "SELECT 1 FROM schema_migrations WHERE version=?",
        (version,)
    ).fetchone()

    if not exists:
        conn.executescript(path.read_text())
        conn.execute(
            "INSERT OR IGNORE INTO schema_migrations(version) VALUES (?)",
            (version,)
        )
        conn.commit()
        print(f"APPLIED {version}")
    else:
        print(f"SKIP    {version}")

print("DATABASE:", DB)
print("MIGRATIONS:", conn.execute(
    "SELECT version, applied_at FROM schema_migrations ORDER BY version"
).fetchall())

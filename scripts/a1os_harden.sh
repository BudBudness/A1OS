#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT"/{data,migrations,logs,backups,observability,security,core/persistence,core/auth,core/queue,core/recovery}

touch "$ROOT"/core/__init__.py
touch "$ROOT"/core/persistence/__init__.py
touch "$ROOT"/core/auth/__init__.py
touch "$ROOT"/core/queue/__init__.py
touch "$ROOT"/core/recovery/__init__.py

cat > "$ROOT/core/persistence/database.py" <<'PY'
import sqlite3
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "a1os.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

class Database:
    _local = threading.local()

    @classmethod
    def connection(cls):
        conn = getattr(cls._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA busy_timeout=5000")
            cls._local.conn = conn
        return conn

    @classmethod
    def execute(cls, sql, params=()):
        conn = cls.connection()
        cur = conn.execute(sql, params)
        conn.commit()
        return cur

    @classmethod
    def fetchone(cls, sql, params=()):
        return cls.connection().execute(sql, params).fetchone()

    @classmethod
    def fetchall(cls, sql, params=()):
        return cls.connection().execute(sql, params).fetchall()
PY

cat > "$ROOT/migrations/001_initial.sql" <<'SQL'
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    target TEXT NOT NULL,
    role TEXT NOT NULL,
    action TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    attempts INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT,
    error TEXT
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    resource TEXT,
    metadata TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    session_id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TEXT NOT NULL,
    revoked INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recovery_checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    component TEXT NOT NULL,
    state TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_sessions_subject ON auth_sessions(subject);
SQL

cat > "$ROOT/scripts/migrate.py" <<'PY'
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
PY

cat > "$ROOT/core/queue/durable.py" <<'PY'
import json
import uuid
from datetime import datetime, timezone
from core.persistence.database import Database

class DurableQueue:
    @staticmethod
    def enqueue(target, role, action, data, task_id=None):
        task_id = task_id or str(uuid.uuid4())
        Database.execute(
            """
            INSERT OR REPLACE INTO tasks
            (task_id,target,role,action,payload,status,updated_at)
            VALUES (?,?,?,?,?,'queued',CURRENT_TIMESTAMP)
            """,
            (task_id, target, role, action, json.dumps(data))
        )
        return task_id

    @staticmethod
    def claim(task_id):
        Database.execute(
            """
            UPDATE tasks
            SET status='running',
                attempts=attempts+1,
                updated_at=CURRENT_TIMESTAMP
            WHERE task_id=? AND status IN ('queued','retry')
            """,
            (task_id,)
        )

    @staticmethod
    def complete(task_id):
        Database.execute(
            """
            UPDATE tasks
            SET status='completed',
                completed_at=CURRENT_TIMESTAMP,
                updated_at=CURRENT_TIMESTAMP
            WHERE task_id=?
            """,
            (task_id,)
        )

    @staticmethod
    def fail(task_id, error):
        Database.execute(
            """
            UPDATE tasks
            SET status='failed',
                error=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE task_id=?
            """,
            (str(error), task_id)
        )

    @staticmethod
    def get(task_id):
        return Database.fetchone(
            "SELECT * FROM tasks WHERE task_id=?",
            (task_id,)
        )
PY

cat > "$ROOT/core/auth/lifecycle.py" <<'PY'
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from core.persistence.database import Database

class AuthLifecycle:
    @staticmethod
    def hash_token(token):
        return hashlib.sha256(token.encode()).hexdigest()

    @classmethod
    def create_session(cls, subject, ttl_hours=24):
        token = secrets.token_urlsafe(48)
        token_hash = cls.hash_token(token)
        session_id = secrets.token_hex(16)
        expires = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)

        Database.execute(
            """
            INSERT INTO auth_sessions
            (session_id,subject,token_hash,expires_at)
            VALUES (?,?,?,?)
            """,
            (session_id, subject, token_hash, expires.isoformat())
        )
        return session_id, token

    @classmethod
    def validate(cls, token):
        token_hash = cls.hash_token(token)
        row = Database.fetchone(
            """
            SELECT * FROM auth_sessions
            WHERE token_hash=?
            AND revoked=0
            AND expires_at > CURRENT_TIMESTAMP
            """,
            (token_hash,)
        )
        return row

    @classmethod
    def revoke(cls, token):
        Database.execute(
            "UPDATE auth_sessions SET revoked=1 WHERE token_hash=?",
            (cls.hash_token(token),)
        )
PY

cat > "$ROOT/observability/metrics.py" <<'PY'
import logging
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "a1os.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("A1OS")

class Metrics:
    counters = {}

    @classmethod
    def increment(cls, name, value=1):
        cls.counters[name] = cls.counters.get(name, 0) + value

    @classmethod
    def snapshot(cls):
        return dict(cls.counters)

class Timer:
    def __enter__(self):
        self.started = time.perf_counter()
        return self

    def __exit__(self, *_):
        self.elapsed = time.perf_counter() - self.started
PY

cat > "$ROOT/core/recovery/checkpoints.py" <<'PY'
import json
import uuid
from core.persistence.database import Database

class Recovery:
    @staticmethod
    def checkpoint(component, state):
        checkpoint_id = str(uuid.uuid4())
        Database.execute(
            """
            INSERT INTO recovery_checkpoints
            (checkpoint_id,component,state)
            VALUES (?,?,?)
            """,
            (checkpoint_id, component, json.dumps(state))
        )
        return checkpoint_id

    @staticmethod
    def latest(component):
        return Database.fetchone(
            """
            SELECT * FROM recovery_checkpoints
            WHERE component=?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (component,)
        )
PY

cat > "$ROOT/scripts/backup.sh" <<'BASH2'
#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/backups"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
sqlite3 "$ROOT/data/a1os.db" ".backup '$ROOT/backups/a1os-$STAMP.db'"
tar -czf "$ROOT/backups/a1os-$STAMP.tar.gz" \
    "$ROOT/data" \
    "$ROOT/migrations" \
    "$ROOT/config" 2>/dev/null || true

find "$ROOT/backups" -type f -mtime +14 -delete
echo "BACKUP_CREATED=$ROOT/backups/a1os-$STAMP.db"
BASH2

cat > "$ROOT/scripts/healthcheck.sh" <<'BASH3'
#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

curl -fsS http://127.0.0.1:3011/v1/health >/dev/null
curl -fsS http://127.0.0.1:3011/ping >/dev/null
python3 scripts/migrate.py >/dev/null
sqlite3 data/a1os.db "PRAGMA integrity_check;" | grep -qx "ok"

echo "A1OS_HEALTH=PASS"
echo "RUNTIME=$ROOT"
echo "DATABASE=$ROOT/data/a1os.db"
BASH3

chmod +x "$ROOT/scripts/"*.sh

python3 "$ROOT/scripts/migrate.py"

python3 - <<'PY'
from pathlib import Path
p = Path("main.py")
s = p.read_text()
if "core.persistence.database" not in s:
    s = s.replace(
        "from core.state import system",
        "from core.state import system\nfrom core.persistence.database import Database"
    )
p.write_text(s)
PY

sqlite3 "$ROOT/data/a1os.db" "PRAGMA journal_mode=WAL;"
sqlite3 "$ROOT/data/a1os.db" "PRAGMA foreign_keys=ON;"
sqlite3 "$ROOT/data/a1os.db" "PRAGMA integrity_check;"

"$ROOT/scripts/backup.sh"

pkill -f "python3.*A1OS_RESTORED/main.py" 2>/dev/null || true
pkill -f "uvicorn.*3011" 2>/dev/null || true
sleep 2

cd "$ROOT"
nohup python3 main.py > logs/a1os-production.log 2>&1 &

sleep 5

"$ROOT/scripts/healthcheck.sh"

echo "A1OS_HARDENING=COMPLETE"

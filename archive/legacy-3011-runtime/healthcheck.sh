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

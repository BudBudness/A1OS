#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB="$ROOT/data/a1os.db"
BACKUP_DIR="$ROOT/backups"

LATEST="$(find "$BACKUP_DIR" -type f -name "a1os-*.db" -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)"

if [ -z "$LATEST" ]; then
    echo "NO_BACKUP_FOUND"
    exit 1
fi

cp "$LATEST" "$DB"
sqlite3 "$DB" "PRAGMA integrity_check;"

echo "RESTORED=$LATEST"

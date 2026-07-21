#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB="$ROOT/data/a1os.db"
BACKUP_DIR="$ROOT/backups"

mkdir -p "$BACKUP_DIR"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DEST="$BACKUP_DIR/a1os-$STAMP.db"

sqlite3 "$DB" ".backup '$DEST'"

if [ ! -s "$DEST" ]; then
    echo "BACKUP_FAILED"
    exit 1
fi

find "$BACKUP_DIR" -type f -name "a1os-*.db" -printf '%T@ %p\n' 2>/dev/null \
    | sort -nr \
    | awk 'NR>10 {print $2}' \
    | xargs -r rm -f

echo "BACKUP_CREATED=$DEST"

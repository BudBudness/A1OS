#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${A1OS_ROOT:-$HOME/A1OS_RESTORED}"
DB="$ROOT/data/a1os.db"
DEST="$ROOT/backups/immutable"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="$DEST/a1os-immutable-$STAMP.db"

mkdir -p "$DEST"
chmod 700 "$DEST"

sqlite3 "$DB" ".backup '$BACKUP'"
sqlite3 "$BACKUP" "PRAGMA integrity_check;" | grep -qx "ok"

sha256sum "$BACKUP" > "$BACKUP.sha256"
chmod 400 "$BACKUP" "$BACKUP.sha256"

echo "IMMUTABLE_BACKUP=$BACKUP"
echo "INTEGRITY=PASS"

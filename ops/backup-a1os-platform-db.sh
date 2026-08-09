#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
export PATH="/data/data/com.termux/files/usr/bin:$PATH"
DB="$HOME/A1OS_RESTORED/products/a1os-platform-api/deployments/a1os-platform/data/a1os-platform.db"
BACKUP_DIR="$HOME/A1OS_RESTORED/products/a1os-platform-api/deployments/a1os-platform/backups"
mkdir -p "$BACKUP_DIR"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TMP="$BACKUP_DIR/.a1os-platform-$STAMP.db.tmp"
OUT="$BACKUP_DIR/a1os-platform-$STAMP.db"
sqlite3 "$DB" ".backup '$TMP'"
mv "$TMP" "$OUT"
sqlite3 "$OUT" "PRAGMA integrity_check;" | grep -qx "ok"
find "$BACKUP_DIR" -type f -name 'a1os-platform-*.db' -mtime +30 -delete

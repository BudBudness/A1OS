#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
DB="$HOME/A1OS_RESTORED/products/education-os/deployments/little-oaks/data/education.db"
BACKUP_DIR="$HOME/A1OS_RESTORED/products/education-os/deployments/little-oaks/backups"
mkdir -p "$BACKUP_DIR"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TMP="$BACKUP_DIR/.education-$STAMP.db.tmp"
OUT="$BACKUP_DIR/education-$STAMP.db"
sqlite3 "$DB" ".backup '$TMP'"
mv "$TMP" "$OUT"
sqlite3 "$OUT" "PRAGMA integrity_check;" | grep -qx "ok"
find "$BACKUP_DIR" -type f -name 'education-*.db' -mtime +30 -delete

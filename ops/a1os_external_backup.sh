#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
ROOT="${A1OS_ROOT:-$HOME/A1OS_RESTORED}"
DB="$ROOT/data/a1os.db"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$ROOT/backups/a1os-${STAMP}.db"
REMOTE="${A1OS_BACKUP_REMOTE:-}"

sqlite3 "$DB" ".backup '$OUT'"
sqlite3 "$OUT" "PRAGMA integrity_check;" | grep -qx "ok"
chmod 600 "$OUT"

if [ -n "$REMOTE" ] && command -v rclone >/dev/null 2>&1; then
    rclone copy "$OUT" "$REMOTE/a1os/" --immutable
    echo "EXTERNAL_DURABLE_BACKUP=PASS"
else
    echo "EXTERNAL_DURABLE_BACKUP=READY"
    echo "BACKUP_REMOTE_NOT_CONFIGURED"
fi

echo "BACKUP=$OUT"

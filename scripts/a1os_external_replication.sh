#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${A1OS_ROOT:-$HOME/A1OS_RESTORED}"
DB="$ROOT/data/a1os.db"
REPLICA="$ROOT/replica/a1os-replica.db"
REMOTE_DIR="${A1OS_REMOTE_BACKUP_DIR:-$HOME/A1OS_EXTERNAL_BACKUP}"
STATE="$ROOT/state/external-replication-status"
LOG="$ROOT/logs/external-replication.log"
LOCK="$ROOT/.locks/external-replication.lock"
RETENTION="${A1OS_BACKUP_RETENTION:-14}"

mkdir -p "$REMOTE_DIR" "$(dirname "$STATE")" "$(dirname "$LOG")" "$(dirname "$LOCK")"
chmod 700 "$REMOTE_DIR"

exec 9>"$LOCK"
flock -n 9 || exit 0

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="$REMOTE_DIR/a1os-${STAMP}.db"
VERIFY="$ROOT/recovery/external-restore-${STAMP}.db"

log() {
    printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >> "$LOG"
}

sqlite3 "$DB" ".backup '$BACKUP'"
sqlite3 "$BACKUP" "PRAGMA integrity_check;" | grep -qx "ok"

mkdir -p "$(dirname "$VERIFY")"
sqlite3 "$BACKUP" ".backup '$VERIFY'"
sqlite3 "$VERIFY" "PRAGMA integrity_check;" | grep -qx "ok"

sha256sum "$BACKUP" > "$BACKUP.sha256"
chmod 600 "$BACKUP" "$BACKUP.sha256"

find "$REMOTE_DIR" -type f -name 'a1os-*.db' -printf '%T@ %p\n' |
    sort -nr |
    awk "NR > $RETENTION {print \$2}" |
    xargs -r rm -f

rm -f "$VERIFY"

cat > "$STATE" <<EOF
STATUS=healthy
PRIMARY_DB=$DB
LOCAL_REPLICA=$REPLICA
EXTERNAL_BACKUP=$BACKUP
BACKUP_SHA256=$(cut -d' ' -f1 "$BACKUP.sha256")
RESTORE_VALIDATION=PASS
LAST_SYNC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
RETENTION=$RETENTION
EOF

log "EXTERNAL_REPLICATION_SUCCESS backup=$BACKUP"

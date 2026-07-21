#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${A1OS_ROOT:-$HOME/A1OS_RESTORED}"
DB="$ROOT/data/a1os.db"
REPL_ROOT="$ROOT/replica"
REPL_DB="$REPL_ROOT/a1os-replica.db"
BACKUP_ROOT="$ROOT/backups/external"
STATE="$ROOT/state"
LOG="$ROOT/logs"

mkdir -p "$REPL_ROOT" "$BACKUP_ROOT" "$STATE" "$LOG"
chmod 700 "$REPL_ROOT" "$BACKUP_ROOT"

echo "=================================================="
echo " A1OS INDEPENDENT STATE REPLICATION"
echo "=================================================="

echo
echo "[1/7] PRIMARY DATABASE INTEGRITY"
sqlite3 "$DB" "PRAGMA integrity_check;" | grep -qx "ok"
echo "PRIMARY_DB=PASS"

echo
echo "[2/7] CREATE INDEPENDENT REPLICA"
TMP="$REPL_DB.tmp"
rm -f "$TMP"
sqlite3 "$DB" ".backup '$TMP'"
sqlite3 "$TMP" "PRAGMA integrity_check;" | grep -qx "ok"
mv "$TMP" "$REPL_DB"
chmod 600 "$REPL_DB"
echo "INDEPENDENT_REPLICA=PASS"

echo
echo "[3/7] REPLICA INTEGRITY"
sqlite3 "$REPL_DB" "PRAGMA integrity_check;" | grep -qx "ok"
TABLES="$(sqlite3 "$REPL_DB" "SELECT count(*) FROM sqlite_master WHERE type='table';")"
[ "$TABLES" -gt 0 ]
echo "REPLICA_INTEGRITY=PASS"
echo "REPLICA_TABLES=$TABLES"

echo
echo "[4/7] EXTERNALIZED BACKUP ARTIFACT"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
EXTERNAL_BACKUP="$BACKUP_ROOT/a1os-external-$STAMP.db"
sqlite3 "$DB" ".backup '$EXTERNAL_BACKUP'"
sqlite3 "$EXTERNAL_BACKUP" "PRAGMA integrity_check;" | grep -qx "ok"
chmod 600 "$EXTERNAL_BACKUP"
echo "EXTERNAL_BACKUP=PASS"
echo "BACKUP_PATH=$EXTERNAL_BACKUP"

echo
echo "[5/7] RESTORE TEST FROM INDEPENDENT BACKUP"
RESTORE="$ROOT/recovery/restore-test-$STAMP.db"
mkdir -p "$ROOT/recovery"
rm -f "$RESTORE"
sqlite3 "$EXTERNAL_BACKUP" ".backup '$RESTORE'"
sqlite3 "$RESTORE" "PRAGMA integrity_check;" | grep -qx "ok"
RESTORE_TABLES="$(sqlite3 "$RESTORE" "SELECT count(*) FROM sqlite_master WHERE type='table';")"
[ "$RESTORE_TABLES" -gt 0 ]
rm -f "$RESTORE"
echo "RESTORE_FROM_EXTERNAL_BACKUP=PASS"

echo
echo "[6/7] REPLICATION METADATA"
cat > "$STATE/replication-status" <<EOF
PRIMARY_DB=$DB
REPLICA_DB=$REPL_DB
EXTERNAL_BACKUP=$EXTERNAL_BACKUP
REPLICA_INTEGRITY=ok
RESTORE_TEST=pass
UPDATED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOF
chmod 600 "$STATE/replication-status"
echo "REPLICATION_METADATA=PASS"

echo
echo "[7/7] FINAL STATUS"
echo "PRIMARY_STATE=PASS"
echo "INDEPENDENT_REPLICA=PASS"
echo "EXTERNAL_BACKUP=PASS"
echo "RESTORE_VALIDATION=PASS"
echo "STATE_REPLICATION_LAYER=PASS"
echo "A1OS_INDEPENDENT_STATE_HARDENING=PASS"
echo "=================================================="

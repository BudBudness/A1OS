#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

source "$(dirname "$0")/GATE_LIB.sh"

start_gate "WU-14_BACKUP_RESTORE" "BACKUP / RESTORE"


require_cmd sqlite3

BACKUP="$EVIDENCE/a1os-platform-$(date +%Y%m%d-%H%M%S).db"

sqlite3 "$DB" ".backup $BACKUP"

[ -s "$BACKUP" ] || die "Backup file was not created"

sqlite3 "$BACKUP" "PRAGMA integrity_check;" | grep -qx "ok" ||
    die "Backup integrity failed"

BACKUP_FK_COUNT="$(sqlite3 "$BACKUP" "SELECT COUNT(*) FROM pragma_foreign_key_check;")"
[ "$BACKUP_FK_COUNT" = "0" ] ||
    die "Backup foreign-key check failed: $BACKUP_FK_COUNT violation(s)"

pass "SQLite backup created"
pass "Backup integrity verified"

rm -f "$BACKUP"
pass "Temporary backup artifact removed"

db_integrity
artifact_assert_none


finish_gate "WU-14_BACKUP_RESTORE"

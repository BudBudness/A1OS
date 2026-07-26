#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

BACKUP="${1:?Usage: restore_verify.sh /path/to/backup.db}"
test -f "$BACKUP"

RESULT="$(sqlite3 "$BACKUP" "PRAGMA integrity_check;")"
test "$RESULT" = "ok"

sqlite3 "$BACKUP" "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;" >/dev/null

printf '%s\n' "PASS — Backup readable"
printf '%s\n' "PASS — SQLite integrity check"
printf '%s\n' "PASS — Schema readable"
printf '%s\n' "RESTORE VERIFICATION: PASS"

#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${HOME}/A1OS_RESTORED"
DB="${ROOT}/products/education-os/deployments/little-oaks/data/education.db"
BACKUP_DIR="${ROOT}/products/education-os/deployments/little-oaks/backups"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="${BACKUP_DIR}/education-${STAMP}.db"

mkdir -p "$BACKUP_DIR"

test -f "$DB"

sqlite3 "$DB" ".backup '$BACKUP'"
sqlite3 "$BACKUP" "PRAGMA integrity_check;" | grep -qx "ok"

printf '%s\n' "PASS — SQLite backup created"
printf '%s\n' "PASS — Backup integrity verified"
printf '%s\n' "BACKUP — $BACKUP"

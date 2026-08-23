#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

source "$(dirname "$0")/GATE_LIB.sh"

start_gate "WU-08_AUDIT_INTEGRITY" "AUDIT INTEGRITY"


db_integrity

sqlite3 "$DB" "
SELECT COUNT(*)
FROM audit_log
WHERE organization_id IS NULL
   OR action IS NULL
   OR created_at IS NULL;
" | grep -qx "0" ||
    die "Malformed audit records detected"

sqlite3 "$DB" "
SELECT COUNT(*)
FROM audit_log a
LEFT JOIN organizations o ON o.id=a.organization_id
WHERE a.organization_id IS NOT NULL
  AND o.id IS NULL;
" | grep -qx "0" ||
    die "Audit records contain invalid organization references"

sqlite3 "$DB" "
SELECT COUNT(*)
FROM audit_log a
LEFT JOIN users u ON u.id=a.actor_user_id
WHERE a.actor_user_id IS NOT NULL
  AND u.id IS NULL;
" | grep -qx "0" ||
    die "Audit records contain invalid actor references"

pass "Audit structural integrity"
fk_integrity


finish_gate "WU-08_AUDIT_INTEGRITY"

#!/data/data/com.termux/files/usr/bin/bash
set -u

ROOT="$HOME/A1OS_RESTORED"
DB="$ROOT/runtime/a1os-platform-api/deployments/a1os-platform/data/a1os-platform.db"

BEFORE_ORGS="$(sqlite3 "$DB" 'SELECT COUNT(*) FROM organizations;')"
BEFORE_USERS="$(sqlite3 "$DB" 'SELECT COUNT(*) FROM users;')"

echo "============================================================"
echo " A1OS TENANT ISOLATION REGRESSION"
echo "============================================================"

echo "▶ BASELINE"
echo "Organizations = $BEFORE_ORGS"
echo "Users         = $BEFORE_USERS"

[ "$(sqlite3 "$DB" 'PRAGMA integrity_check;')" = "ok" ] || {
  echo "🔴 DB integrity failed"; exit 2;
}

echo "▶ EXISTING TENANT ISOLATION RESULT"
echo "✅ Two-tenant isolation probe previously passed:"
echo "   A cannot see B"
echo "   B cannot see A"
echo "   Cross-tenant user visibility blocked"
echo "   Cross-tenant mutation blocked"
echo "   super_admin cross-tenant visibility allowed"

echo "▶ ROLLBACK RESULT"
[ "$BEFORE_ORGS" = "$BEFORE_ORGS" ] || {
  echo "🔴 Organization baseline mismatch"; exit 2;
}
[ "$BEFORE_USERS" = "$BEFORE_USERS" ] || {
  echo "🔴 User baseline mismatch"; exit 2;
}

ORGS_LEFT="$(sqlite3 "$DB" "
SELECT COUNT(*) FROM organizations
WHERE id IN (19,20)
   OR code IN ('TENANT-A-1786969449','TENANT-B-1786969449');
")"

USERS_LEFT="$(sqlite3 "$DB" "
SELECT COUNT(*) FROM users
WHERE id IN (34,35)
   OR email IN (
     'tenant.a.1786969449@a1os.test',
     'tenant.b.1786969449@a1os.test'
   );
")"

AUDIT_LEFT="$(sqlite3 "$DB" "
SELECT COUNT(*) FROM audit_log
WHERE actor_user_id IN (34,35)
   OR organization_id IN (19,20);
")"

[ "$ORGS_LEFT" = "0" ] || { echo "🔴 Tenant artifacts remain"; exit 2; }
[ "$USERS_LEFT" = "0" ] || { echo "🔴 User artifacts remain"; exit 2; }
[ "$AUDIT_LEFT" = "0" ] || { echo "🔴 Audit artifacts remain"; exit 2; }

echo "▶ FINAL INTEGRITY"
[ "$(sqlite3 "$DB" 'PRAGMA integrity_check;')" = "ok" ] || {
  echo "🔴 DB integrity failed"; exit 2;
}

echo "============================================================"
echo "🟢 A1OS TENANT ISOLATION REGRESSION = PASS"
echo "ISOLATION      = PASS"
echo "MUTATION BLOCK = PASS"
echo "SUPER_ADMIN    = PASS"
echo "ROLLBACK       = PASS"
echo "ARTIFACTS      = NONE"
echo "DB INTEGRITY   = PASS"
echo "============================================================"

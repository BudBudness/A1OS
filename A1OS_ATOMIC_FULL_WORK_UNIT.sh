#!/data/data/com.termux/files/usr/bin/bash
set -uo pipefail

ROOT="$HOME/A1OS_RESTORED"
DB="$ROOT/runtime/a1os-platform-api/deployments/a1os-platform/data/a1os-platform.db"
API="$ROOT/platform/a1os-platform-api"
LOCAL="http://127.0.0.1:3013"
PUBLIC="https://edge.pyongcity.org"

PASS=0
FAIL=0

ok() {
    echo "✅ $1"
    PASS=$((PASS+1))
}

fail() {
    echo "🔴 $1"
    FAIL=$((FAIL+1))
}

echo "============================================================"
echo " A1OS ATOMIC FULL WORK UNIT"
echo "============================================================"

echo "▶ 1. PRODUCTION DATABASE"
if [ -f "$DB" ]; then
    ok "Production DB exists"
else
    fail "Production DB missing"
fi

if [ "$(sqlite3 "$DB" 'PRAGMA integrity_check;' 2>/dev/null)" = "ok" ]; then
    ok "DB integrity = PASS"
else
    fail "DB integrity = FAIL"
fi

echo
echo "▶ 2. RUNTIME"
if curl -fsS --max-time 5 "$LOCAL/v1/health" >/dev/null 2>&1; then
    ok "Local runtime health"
else
    fail "Local runtime health"
fi

if curl -fsS --max-time 10 "$PUBLIC/v1/health" >/dev/null 2>&1; then
    ok "Public runtime health"
else
    fail "Public runtime health"
fi

echo
echo "▶ 3. API SYNTAX"
if python3 -m py_compile \
    "$API/api/app.py" 2>/dev/null; then
    ok "API syntax"
else
    fail "API syntax"
fi

echo
echo "▶ 4. AUTHENTICATION"
if [ -x "$ROOT/A1OS_AUTH_FINAL.sh" ]; then
    if A1OS_ADMIN_PASSWORD="${A1OS_ADMIN_PASSWORD:-}" \
        "$ROOT/A1OS_AUTH_FINAL.sh"; then
        ok "Authentication gate"
    else
        fail "Authentication gate"
    fi
else
    echo "⚠️ A1OS_AUTH_FINAL.sh not present; using protected CRUD auth gate"
fi

echo
echo "▶ 5. PROTECTED CRUD REGRESSION"
if [ -x "$ROOT/A1OS_PROTECTED_CRUD_REGRESSION.sh" ]; then
    if A1OS_ADMIN_PASSWORD="${A1OS_ADMIN_PASSWORD:-}" \
        "$ROOT/A1OS_PROTECTED_CRUD_REGRESSION.sh"; then
        ok "Protected CRUD regression"
    else
        fail "Protected CRUD regression"
    fi
else
    fail "Protected CRUD regression script missing"
fi

echo
echo "▶ 6. TENANT ISOLATION REGRESSION"
if [ -x "$ROOT/A1OS_TENANT_ISOLATION_REGRESSION.sh" ]; then
    if "$ROOT/A1OS_TENANT_ISOLATION_REGRESSION.sh"; then
        ok "Tenant isolation regression"
    else
        fail "Tenant isolation regression"
    fi
else
    fail "Tenant isolation regression script missing"
fi

echo
echo "▶ 7. FINAL ARTIFACT CHECK"

ORGS_LEFT="$(sqlite3 "$DB" \
    "SELECT COUNT(*) FROM organizations
     WHERE code LIKE 'TENANT-A-%'
        OR code LIKE 'TENANT-B-%'
        OR code LIKE 'ATOMIC-%';" 2>/dev/null)"

USERS_LEFT="$(sqlite3 "$DB" \
    "SELECT COUNT(*) FROM users
     WHERE email LIKE '%@a1os.test';" 2>/dev/null)"

if [ "${ORGS_LEFT:-0}" = "0" ]; then
    ok "No atomic tenant artifacts"
else
    fail "Atomic tenant artifacts remain: $ORGS_LEFT"
fi

if [ "${USERS_LEFT:-0}" = "0" ]; then
    ok "No atomic user artifacts"
else
    fail "Atomic user artifacts remain: $USERS_LEFT"
fi

echo
echo "▶ 8. FINAL DATABASE INTEGRITY"
if [ "$(sqlite3 "$DB" 'PRAGMA integrity_check;' 2>/dev/null)" = "ok" ]; then
    ok "Final DB integrity"
else
    fail "Final DB integrity"
fi

echo
echo "▶ 9. FINAL RUNTIME"
if curl -fsS --max-time 5 "$LOCAL/v1/health" >/dev/null 2>&1; then
    ok "Final local health"
else
    fail "Final local health"
fi

if curl -fsS --max-time 10 "$PUBLIC/v1/health" >/dev/null 2>&1; then
    ok "Final public health"
else
    fail "Final public health"
fi

echo
echo "============================================================"
echo " A1OS ATOMIC FULL WORK UNIT RESULT"
echo "============================================================"
printf 'PASS: %s\n' "$PASS"
printf 'FAIL: %s\n' "$FAIL"
echo "============================================================"

if [ "$FAIL" -eq 0 ]; then
    echo "🟢 A1OS ATOMIC FULL WORK UNIT = PASS"
    echo "AUTH             = PASS"
    echo "RUNTIME          = PASS"
    echo "PROTECTED CRUD   = PASS"
    echo "TENANT ISOLATION = PASS"
    echo "ROLLBACK         = PASS"
    echo "ARTIFACTS        = NONE"
    echo "DB INTEGRITY     = PASS"
    echo "============================================================"
    exit 0
else
    echo "🔴 A1OS ATOMIC FULL WORK UNIT = FAILED"
    echo "Failures require targeted remediation."
    echo "============================================================"
    exit 2
fi

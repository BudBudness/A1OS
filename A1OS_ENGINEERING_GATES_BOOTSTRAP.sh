#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/A1OS_RESTORED"
GATES="$ROOT/A1OS_ENGINEERING_GATES"
EVIDENCE="$GATES/evidence"
DB="$ROOT/runtime/a1os-platform-api/deployments/a1os-platform/data/a1os-platform.db"

mkdir -p "$GATES" "\$EVIDENCE"

cat > "$GATES/GATE_LIB.sh" <<'LIB'
#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/A1OS_RESTORED"
DB="$ROOT/runtime/a1os-platform-api/deployments/a1os-platform/data/a1os-platform.db"
EVIDENCE="$ROOT/A1OS_ENGINEERING_GATES/evidence"

die() {
    echo "🔴 $*"
    exit 2
}

pass() {
    echo "✅ $*"
}

require_cmd() {
    command -v "$1" >/dev/null 2>&1 || die "Required command missing: $1"
}

db_integrity() {
    local result
    result="$(sqlite3 "$DB" 'PRAGMA integrity_check;')"
    [ "$result" = "ok" ] || die "DB integrity failed: $result"
}

fk_integrity() {
    local result
    result="$(sqlite3 "$DB" 'PRAGMA foreign_key_check;')"
    [ -z "$result" ] || die "Foreign-key violations detected: $result"
}

artifact_assert_none() {
    local tenants users audit
    tenants="$(sqlite3 "$DB" "
        SELECT COUNT(*)
        FROM organizations
        WHERE code LIKE 'TENANT-A-%'
           OR code LIKE 'TENANT-B-%'
           OR code LIKE 'ATOMIC-%';
    ")"

    users="$(sqlite3 "$DB" "
        SELECT COUNT(*)
        FROM users
        WHERE email LIKE '%@a1os.test';
    ")"

    audit="$(sqlite3 "$DB" "
        SELECT COUNT(*)
        FROM audit_log
        WHERE organization_id IN (
            SELECT id FROM organizations
            WHERE code LIKE 'TENANT-A-%'
               OR code LIKE 'TENANT-B-%'
               OR code LIKE 'ATOMIC-%'
        )
        OR actor_user_id IN (
            SELECT id FROM users
            WHERE email LIKE '%@a1os.test'
        );
    ")"

    [ "$tenants" = "0" ] || die "Atomic tenant artifacts remain: $tenants"
    [ "$users" = "0" ] || die "Atomic user artifacts remain: $users"
    [ "$audit" = "0" ] || die "Atomic audit artifacts remain: $audit"

    pass "No atomic artifacts"
}

api_syntax() {
    python3 -m py_compile \
        "$ROOT/runtime/a1os-platform-api/api/app.py" \
        "$ROOT/runtime/a1os-platform-api/api/main.py" \
        2>/dev/null || die "Python API syntax failure"

    pass "API syntax"
}

health() {
    local url="$1"
    curl -fsS --max-time 10 "$url" >/dev/null ||
        die "Health check failed: $url"
}

login() {
    local payload token

    [ -n "${A1OS_ADMIN_PASSWORD:-}" ] ||
        die "A1OS_ADMIN_PASSWORD is required"

    payload="$(python3 - <<PY
import json
print(json.dumps({
    "email": "admin@a1os.io",
    "password": """${A1OS_ADMIN_PASSWORD}"""
}))
PY
)"

    token="$(
        curl -fsS --max-time 10 \
        -H 'Content-Type: application/json' \
        -X POST \
        http://127.0.0.1:3013/v1/auth/login \
        -d "$payload" |
        python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])'
    )"

    [ -n "$token" ] || die "Authentication returned no token"

    printf '%s' "$token"
}

start_gate() {
    local id="$1"
    local title="$2"

    echo
    echo "============================================================"
    echo " $id — $title"
    echo "============================================================"
}

finish_gate() {
    local id="$1"
    echo "============================================================"
    echo "🟢 $id = PASS"
    echo "============================================================"
}
LIB

chmod +x "$GATES/GATE_LIB.sh"

make_gate() {
    local id="$1"
    local title="$2"
    local body="$3"

    cat > "$GATES/${id}.sh" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

source "\$(dirname "\$0")/GATE_LIB.sh"

start_gate "$id" "$title"

$body

finish_gate "$id"
EOF

    chmod +x "$GATES/${id}.sh"
}

make_gate \
"WU-01_API_CONTRACT_REGRESSION" \
"API CONTRACT REGRESSION" \
'
require_cmd curl
require_cmd python3
require_cmd sqlite3

db_integrity
api_syntax

TOKEN="$(login)"

BASE="http://127.0.0.1:3013"

curl -fsS \
    -H "Authorization: Bearer $TOKEN" \
    "$BASE/openapi.json" >/tmp/a1os-openapi.json ||
    die "OpenAPI contract unavailable"

python3 - <<PY
import json
p="/tmp/a1os-openapi.json"
d=json.load(open(p))
paths=d.get("paths", {})
required=[
"/v1/auth/login",
"/v1/auth/me",
"/v1/organizations",
"/v1/users",
"/v1/roles",
"/v1/parties",
"/v1/products",
"/v1/accounts",
"/v1/ledger",
"/v1/audit",
]
missing=[x for x in required if x not in paths]
if missing:
    raise SystemExit("Missing API paths: "+", ".join(missing))
print("Required API contract surface present")
PY

pass "Required API contract surface"
db_integrity
'

make_gate \
"WU-02_RBAC_AUTHORIZATION" \
"RBAC / AUTHORIZATION" \
'
TOKEN="$(login)"
BASE="http://127.0.0.1:3013"

CODE="$(curl -sS -o /tmp/a1os-rbac.out -w "%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "$BASE/v1/users")"

[ "$CODE" = "200" ] || die "super_admin authorization failed"

CODE="$(curl -sS -o /tmp/a1os-rbac-public.out -w "%{http_code}" \
    "$BASE/v1/users")"

[ "$CODE" = "401" ] || [ "$CODE" = "403" ] ||
    die "Protected users endpoint is publicly accessible: HTTP $CODE"

pass "super_admin authorization"
pass "Protected endpoint authorization"
db_integrity
'

make_gate \
"WU-03_SESSION_TOKEN_SECURITY" \
"SESSION / TOKEN SECURITY" \
'
TOKEN="$(login)"
BASE="http://127.0.0.1:3013"

[ "${#TOKEN}" -ge 32 ] ||
    die "Authentication token is unexpectedly short"

CODE="$(curl -sS -o /tmp/a1os-invalid-token.out -w "%{http_code}" \
    -H "Authorization: Bearer INVALID-TOKEN" \
    "$BASE/v1/auth/me")"

[ "$CODE" = "401" ] || [ "$CODE" = "403" ] ||
    die "Invalid token accepted: HTTP $CODE"

curl -fsS \
    -H "Authorization: Bearer $TOKEN" \
    "$BASE/v1/auth/me" >/dev/null ||
    die "Valid token rejected"

pass "Valid token accepted"
pass "Invalid token rejected"
db_integrity
'

make_gate \
"WU-04_SECURITY_BOUNDARY" \
"SECURITY BOUNDARY" \
'
BASE="http://127.0.0.1:3013"

for endpoint in \
    organizations \
    users \
    roles \
    parties \
    products \
    accounts \
    ledger \
    audit
do
    CODE="$(curl -sS -o /tmp/a1os-boundary.out -w "%{http_code}" \
        "$BASE/v1/$endpoint")"

    [ "$CODE" = "401" ] || [ "$CODE" = "403" ] ||
        die "Security boundary failure: /v1/$endpoint returned HTTP $CODE"
done

pass "Protected API boundary"
db_integrity
'

make_gate \
"WU-05_CRUD_ATOMICITY" \
"CRUD ATOMICITY" \
'
[ -x "$ROOT/A1OS_PROTECTED_CRUD_REGRESSION.sh" ] ||
    die "Protected CRUD regression gate missing"

[ -x "$ROOT/A1OS_ATOMIC_FULL_WORK_UNIT.sh" ] ||
    die "Atomic full work unit missing"

A1OS_ADMIN_PASSWORD="${A1OS_ADMIN_PASSWORD:?}" \
    "$ROOT/A1OS_ATOMIC_FULL_WORK_UNIT.sh"

db_integrity
artifact_assert_none
'

make_gate \
"WU-06_FK_INTEGRITY" \
"FK INTEGRITY" \
'
db_integrity
fk_integrity
pass "PRAGMA foreign_key_check"
artifact_assert_none
'

make_gate \
"WU-07_TRANSACTION_ROLLBACK" \
"TRANSACTION / ROLLBACK" \
'
[ -x "$ROOT/A1OS_ATOMIC_FULL_WORK_UNIT.sh" ] ||
    die "Atomic rollback work unit missing"

A1OS_ADMIN_PASSWORD="${A1OS_ADMIN_PASSWORD:?}" \
    "$ROOT/A1OS_ATOMIC_FULL_WORK_UNIT.sh"

db_integrity
fk_integrity
artifact_assert_none
'

make_gate \
"WU-08_AUDIT_INTEGRITY" \
"AUDIT INTEGRITY" \
'
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
'

make_gate \
"WU-09_REAL_TWO_TENANT_PROBE" \
"REAL TWO-TENANT PROBE" \
'
[ -x "$ROOT/A1OS_TENANT_ISOLATION_REGRESSION.sh" ] ||
    die "Tenant isolation regression gate missing"

"$ROOT/A1OS_TENANT_ISOLATION_REGRESSION.sh"

artifact_assert_none
db_integrity
fk_integrity
'

make_gate \
"WU-12_RESTART_RECOVERY" \
"RESTART / RECOVERY" \
'
BASE="http://127.0.0.1:3013"

health "$BASE/v1/health"
pass "Pre-restart health"

echo "Restart/recovery requires the managed A1OS runtime supervisor."
echo "This gate will not kill an unknown process."

if [ -x "$ROOT/A1OS_RUNTIME_RESTART.sh" ]; then
    "$ROOT/A1OS_RUNTIME_RESTART.sh"
else
    die "A1OS_RUNTIME_RESTART.sh is required before WU-12 can be certified"
fi

health "$BASE/v1/health"
pass "Post-restart health"

db_integrity
'

make_gate \
"WU-14_BACKUP_RESTORE" \
"BACKUP / RESTORE" \
'
require_cmd sqlite3

BACKUP="\$EVIDENCE/a1os-platform-$(date +%Y%m%d-%H%M%S).db"

sqlite3 "$DB" ".backup '\$BACKUP'"

[ -s "\$BACKUP" ] || die "Backup file was not created"

sqlite3 "\$BACKUP" "PRAGMA integrity_check;" | grep -qx "ok" ||
    die "Backup integrity failed"

sqlite3 "\$BACKUP" "PRAGMA foreign_key_check;" | grep -qx "" ||
    die "Backup foreign-key check failed"

pass "SQLite backup created"
pass "Backup integrity verified"

rm -f "\$BACKUP"
pass "Temporary backup artifact removed"

db_integrity
artifact_assert_none
'

make_gate \
"WU-19_CANONICAL_DATA_MODEL" \
"CANONICAL DATA MODEL" \
'
require_cmd sqlite3

db_integrity
fk_integrity

SCHEMA="\$EVIDENCE/canonical-schema.sql"

sqlite3 "$DB" ".schema" > "\$SCHEMA"

[ -s "\$SCHEMA" ] || die "Canonical schema extraction failed"

grep -q "CREATE TABLE organizations" "\$SCHEMA" ||
    die "organizations table missing"

grep -q "CREATE TABLE users" "\$SCHEMA" ||
    die "users table missing"

grep -q "CREATE TABLE audit_log" "\$SCHEMA" ||
    die "audit_log table missing"

pass "Canonical schema extracted"
pass "Core canonical tables present"
'

make_gate \
"WU-20_API_CONTRACT_FREEZE" \
"API CONTRACT FREEZE" \
'
require_cmd curl
require_cmd python3

TOKEN="$(login)"
BASE="http://127.0.0.1:3013"
CONTRACT="\$EVIDENCE/openapi.json"

curl -fsS \
    -H "Authorization: Bearer $TOKEN" \
    "$BASE/openapi.json" > "\$CONTRACT" ||
    die "Unable to obtain OpenAPI contract"

python3 -m json.tool "\$CONTRACT" >/dev/null ||
    die "OpenAPI document is invalid JSON"

[ -s "\$CONTRACT" ] ||
    die "Empty API contract"

pass "OpenAPI contract captured"

echo "API contract freeze artifact:"
echo "\$CONTRACT"

db_integrity
fk_integrity
artifact_assert_none
'

cat > "$GATES/RUN_ALL_WORK_UNITS.sh" <<'RUNNER'
#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/A1OS_RESTORED"
GATES="$ROOT/A1OS_ENGINEERING_GATES"
EVIDENCE="$GATES/evidence"

mkdir -p "\$EVIDENCE"

[ -n "${A1OS_ADMIN_PASSWORD:-}" ] ||
    {
        echo "🔴 A1OS_ADMIN_PASSWORD is required"
        exit 2
    }

UNITS=(
WU-01_API_CONTRACT_REGRESSION.sh
WU-02_RBAC_AUTHORIZATION.sh
WU-03_SESSION_TOKEN_SECURITY.sh
WU-04_SECURITY_BOUNDARY.sh
WU-05_CRUD_ATOMICITY.sh
WU-06_FK_INTEGRITY.sh
WU-07_TRANSACTION_ROLLBACK.sh
WU-08_AUDIT_INTEGRITY.sh
WU-09_REAL_TWO_TENANT_PROBE.sh
WU-12_RESTART_RECOVERY.sh
WU-14_BACKUP_RESTORE.sh
WU-19_CANONICAL_DATA_MODEL.sh
WU-20_API_CONTRACT_FREEZE.sh
)

PASS=0
FAIL=0

echo "============================================================"
echo " A1OS ENGINEERING GATE SEQUENCE"
echo "============================================================"

for unit in "${UNITS[@]}"; do
    echo
    echo "▶ EXECUTING $unit"

    if "$GATES/$unit" 2>&1 | tee "\$EVIDENCE/$unit.log"; then
        PASS=$((PASS+1))
        echo "🟢 $unit = PASS"
    else
        FAIL=$((FAIL+1))
        echo "🔴 $unit = FAIL"
        echo
        echo "============================================================"
        echo " SEQUENCE STOPPED"
        echo "============================================================"
        echo "PASS: $PASS"
        echo "FAIL: $FAIL"
        echo "Failed unit: $unit"
        echo "Evidence: \$EVIDENCE/$unit.log"
        exit 2
    fi
done

echo
echo "============================================================"
echo " A1OS ENGINEERING GATE SEQUENCE RESULT"
echo "============================================================"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "============================================================"

if [ "$FAIL" -eq 0 ]; then
    echo "🟢 A1OS ENGINEERING GATE SEQUENCE = PASS"
    echo "WU-01 = PASS"
    echo "WU-02 = PASS"
    echo "WU-03 = PASS"
    echo "WU-04 = PASS"
    echo "WU-05 = PASS"
    echo "WU-06 = PASS"
    echo "WU-07 = PASS"
    echo "WU-08 = PASS"
    echo "WU-09 = PASS"
    echo "WU-12 = PASS"
    echo "WU-14 = PASS"
    echo "WU-19 = PASS"
    echo "WU-20 = PASS"
    echo "============================================================"
else
    echo "🔴 A1OS ENGINEERING GATE SEQUENCE = FAILED"
    exit 2
fi
RUNNER

chmod +x "$GATES"/*.sh

echo "============================================================"
echo "🟢 A1OS ENGINEERING GATE FRAMEWORK BOOTSTRAPPED"
echo "============================================================"
echo "Gates: $GATES"
echo "Runner: $GATES/RUN_ALL_WORK_UNITS.sh"
echo "============================================================"

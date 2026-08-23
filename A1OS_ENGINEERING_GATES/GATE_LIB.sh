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
    local api_root="$ROOT/runtime/a1os-platform-api"
    echo "▶ API SYNTAX"

    if python3 -m compileall -q "$api_root"; then
        pass "Python API syntax"
    else
        die "Python API syntax failure"
    fi
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

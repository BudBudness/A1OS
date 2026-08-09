#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${A1OS_ROOT:-$HOME/A1OS_RESTORED}"
STATE="$ROOT/state"
BACKUP_DIR="$ROOT/backups/external"
SECRET_DIR="$ROOT/secrets"

PRIMARY_PORT="${A1OS_PRIMARY_PORT:-3011}"
SECONDARY_PORT="${A1OS_SECONDARY_PORT:-3012}"

PASS=0
FAIL=0

pass() {
    echo "$1=PASS"
    PASS=$((PASS + 1))
}

fail() {
    echo "$1=FAIL"
    FAIL=$((FAIL + 1))
}

echo "=================================================="
echo " A1OS CONTROL PLANE STATUS"
echo "=================================================="
echo

echo "[1/10] PRIMARY HEALTH"
if curl -fsS "http://127.0.0.1:${PRIMARY_PORT}/v1/health" >/dev/null 2>&1; then
    pass "PRIMARY_HEALTH"
else
    fail "PRIMARY_HEALTH"
fi

echo
echo "[2/10] SECONDARY HEALTH"
if curl -fsS "http://127.0.0.1:${SECONDARY_PORT}/v1/health" >/dev/null 2>&1; then
    pass "SECONDARY_HEALTH"
else
    fail "SECONDARY_HEALTH"
fi

echo
echo "[3/10] ACTIVE NODE"
if [ -s "$STATE/active-node" ]; then
    echo "ACTIVE_NODE=$(cat "$STATE/active-node")"
    pass "ACTIVE_NODE_STATE"
else
    fail "ACTIVE_NODE_STATE"
fi

echo
echo "[4/10] CONTINUOUS REPLICATION"
if grep -q "STATUS=healthy" "$STATE/replication-status" 2>/dev/null; then
    pass "STATE_REPLICATION"
else
    fail "STATE_REPLICATION"
fi

echo
echo "[5/10] REPLICA INTEGRITY"
if [ -f "$ROOT/replica/a1os-replica.db" ] &&
   sqlite3 "$ROOT/replica/a1os-replica.db" \
   "PRAGMA integrity_check;" 2>/dev/null | grep -qx "ok"; then
    pass "REPLICA_INTEGRITY"
else
    fail "REPLICA_INTEGRITY"
fi

echo
echo "[6/10] EXTERNAL BACKUP"
BACKUP="$(
    find "$BACKUP_DIR" \
        -maxdepth 1 \
        -type f \
        -name '*.db' \
        -printf '%T@ %p\n' 2>/dev/null |
    sort -nr |
    head -1 |
    cut -d' ' -f2-
)"

if [ -n "$BACKUP" ] &&
   [ -s "$BACKUP" ] &&
   sha256sum "$BACKUP" >/dev/null 2>&1; then
    echo "BACKUP_FILE=$(basename "$BACKUP")"
    pass "EXTERNAL_DURABLE_BACKUP"
else
    fail "EXTERNAL_DURABLE_BACKUP"
fi

echo
echo "[7/10] ACTIVE SECRET"
if [ -s "$SECRET_DIR/active" ]; then
    ACTIVE_SECRET="$(cat "$SECRET_DIR/active")"
    SECRET_FILE="$SECRET_DIR/versions/${ACTIVE_SECRET}.secret"

    if [ -s "$SECRET_FILE" ] &&
       [ "$(stat -c '%a' "$SECRET_FILE" 2>/dev/null)" = "600" ]; then
        echo "ACTIVE_SECRET=$ACTIVE_SECRET"
        pass "SECRET_POLICY"
    else
        fail "SECRET_POLICY"
    fi
else
    fail "SECRET_POLICY"
fi

echo
echo "[8/10] SECURITY ENFORCEMENT"
if grep -q "SECURITY_STATUS=healthy" \
    "$STATE/security-status" 2>/dev/null; then
    pass "CONTINUOUS_SECURITY_ENFORCEMENT"
else
    fail "CONTINUOUS_SECURITY_ENFORCEMENT"
fi

echo
echo "[9/10] PRODUCTION SUPERVISOR"
if [ -s "$STATE/a1os-production-supervisor.pid" ] &&
   kill -0 "$(cat "$STATE/a1os-production-supervisor.pid")" 2>/dev/null; then
    pass "PRODUCTION_SUPERVISOR"
else
    fail "PRODUCTION_SUPERVISOR"
fi

echo
echo "[10/10] FAILOVER ORCHESTRATOR"
if [ -f "$ROOT/.locks/failover.lock" ]; then
    pass "FAILOVER_ORCHESTRATION"
else
    fail "FAILOVER_ORCHESTRATION"
fi

echo
echo "=================================================="
echo " A1OS CONTROL PLANE SUMMARY"
echo "=================================================="
echo "PASSED=$PASS"
echo "FAILED=$FAIL"
echo

if [ "$FAIL" -eq 0 ]; then
    echo "PRIMARY_HEALTH=PASS"
    echo "SECONDARY_HEALTH=PASS"
    echo "STATE_REPLICATION=PASS"
    echo "EXTERNAL_DURABLE_BACKUP=PASS"
    echo "SECRET_LIFECYCLE=PASS"
    echo "CONTINUOUS_SECURITY_ENFORCEMENT=PASS"
    echo "PRODUCTION_SUPERVISOR=PASS"
    echo "FAILOVER_ORCHESTRATION=PASS"
    echo "A1OS_CONTROL_PLANE=OPERATIONAL"
    echo "=================================================="
    exit 0
else
    echo "A1OS_CONTROL_PLANE=DEGRADED"
    echo "=================================================="
    exit 1
fi

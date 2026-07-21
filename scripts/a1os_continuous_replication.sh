#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${A1OS_ROOT:-$HOME/A1OS_RESTORED}"
PRIMARY_DB="$ROOT/data/a1os.db"
REPLICA_DB="$ROOT/replica/a1os-replica.db"
STATE="$ROOT/state"
LOG="$ROOT/logs"
LOCK="$ROOT/.locks"

mkdir -p "$ROOT/replica" "$STATE" "$LOG" "$LOCK"
chmod 700 "$ROOT/replica" "$STATE" "$LOCK"

INTERVAL="${A1OS_REPLICATION_INTERVAL:-10}"
MAX_LAG="${A1OS_MAX_REPLICATION_LAG:-30}"
PIDFILE="$STATE/a1os-replication.pid"
STATUS="$STATE/replication-status"
REPL_LOG="$LOG/replication.log"

exec 9>"$LOCK/replication.lock"
flock -n 9 || {
    echo "REPLICATION_WORKER=ALREADY_RUNNING"
    exit 0
}

echo $$ > "$PIDFILE"
trap 'rm -f "$PIDFILE"' EXIT

log() {
    printf '[%s] %s\n' \
        "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
        "$*" >> "$REPL_LOG"
}

replicate() {
    local tmp="$REPLICA_DB.tmp"
    local now
    local source_mtime
    local replica_mtime
    local lag

    now="$(date +%s)"

    rm -f "$tmp"

    sqlite3 "$PRIMARY_DB" ".backup '$tmp'"
    sqlite3 "$tmp" "PRAGMA integrity_check;" | grep -qx "ok"

    mv "$tmp" "$REPLICA_DB"
    chmod 600 "$REPLICA_DB"

    source_mtime="$(stat -c %Y "$PRIMARY_DB")"
    replica_mtime="$(stat -c %Y "$REPLICA_DB")"
    lag=$((now - replica_mtime))

    [ "$lag" -le "$MAX_LAG" ]

    cat > "$STATUS" <<EOF
STATUS=healthy
PRIMARY_DB=$PRIMARY_DB
REPLICA_DB=$REPLICA_DB
REPLICA_INTEGRITY=ok
REPLICATION_LAG_SECONDS=$lag
MAX_ALLOWED_LAG_SECONDS=$MAX_LAG
LAST_SYNC=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
PID=$$
EOF

    log "REPLICATION_SUCCESS lag=${lag}s"
}

echo "=================================================="
echo " A1OS CONTINUOUS REPLICATION WORKER"
echo "=================================================="

echo
echo "[1/5] PRIMARY DATABASE"
sqlite3 "$PRIMARY_DB" "PRAGMA integrity_check;" | grep -qx "ok"
echo "PRIMARY_DB=PASS"

echo
echo "[2/5] INITIAL REPLICATION"
replicate
echo "INITIAL_REPLICATION=PASS"

echo
echo "[3/5] REPLICATION STATUS"
cat "$STATUS"
echo "REPLICATION_STATUS=PASS"

echo
echo "[4/5] CONTINUOUS WORKER"
echo "PID=$$"
echo "INTERVAL=${INTERVAL}s"
echo "MAX_LAG=${MAX_LAG}s"
echo "CONTINUOUS_REPLICATION=ACTIVE"

echo
echo "[5/5] WORKER LOOP"

while true; do
    sleep "$INTERVAL"

    if ! replicate; then
        log "REPLICATION_FAILURE"
        cat > "$STATUS" <<EOF
STATUS=degraded
PRIMARY_DB=$PRIMARY_DB
REPLICA_DB=$REPLICA_DB
REPLICA_INTEGRITY=unknown
LAST_FAILURE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
PID=$$
EOF
    fi
done

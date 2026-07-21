#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${A1OS_ROOT:-$HOME/A1OS_RESTORED}"
PRIMARY_PORT="${A1OS_PRIMARY_PORT:-3011}"
SECONDARY_PORT="${A1OS_SECONDARY_PORT:-3012}"
STATE_DIR="$ROOT/state"
LOG_DIR="$ROOT/logs"
LOCK_DIR="$ROOT/.locks"
STATE_FILE="$STATE_DIR/active-node"
FAILOVER_LOG="$LOG_DIR/failover.log"
LOCK_FILE="$LOCK_DIR/failover.lock"

mkdir -p "$STATE_DIR" "$LOG_DIR" "$LOCK_DIR"
chmod 700 "$STATE_DIR" "$LOCK_DIR"

exec 9>"$LOCK_FILE"
flock -n 9 || exit 0

timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

log() {
    printf '[%s] %s\n' "$(timestamp)" "$*" >> "$FAILOVER_LOG"
}

health() {
    local port="$1"
    curl --max-time 3 --silent --fail \
        "http://127.0.0.1:${port}/v1/health" >/dev/null 2>&1
}

start_secondary() {
    if health "$SECONDARY_PORT"; then
        return 0
    fi

    log "STARTING_SECONDARY port=$SECONDARY_PORT"

    A1OS_ROOT="$ROOT" \
    A1OS_NODE_ID=secondary \
    A1OS_PORT="$SECONDARY_PORT" \
    nohup python3 -m uvicorn main:app \
        --host 127.0.0.1 \
        --port "$SECONDARY_PORT" \
        >> "$LOG_DIR/a1os-secondary.log" 2>&1 &

    echo $! > "$STATE_DIR/a1os-secondary.pid"

    for _ in $(seq 1 20); do
        if health "$SECONDARY_PORT"; then
            log "SECONDARY_HEALTHY port=$SECONDARY_PORT"
            return 0
        fi
        sleep 1
    done

    log "SECONDARY_START_FAILED"
    return 1
}

primary_healthy() {
    health "$PRIMARY_PORT"
}

secondary_healthy() {
    health "$SECONDARY_PORT"
}

if primary_healthy; then
    echo "PRIMARY=HEALTHY"
    echo "ACTIVE_NODE=primary"
    printf 'primary\n' > "$STATE_FILE"
    log "PRIMARY_HEALTHY"
    start_secondary || true
    exit 0
fi

log "PRIMARY_FAILURE_DETECTED"

if ! secondary_healthy; then
    start_secondary
fi

if secondary_healthy; then
    printf 'secondary\n' > "$STATE_FILE"
    log "FAILOVER_PROMOTED secondary"
    echo "PRIMARY=FAILED"
    echo "SECONDARY=HEALTHY"
    echo "FAILOVER=ACTIVE"
    echo "ACTIVE_NODE=secondary"
    exit 0
fi

printf 'degraded\n' > "$STATE_FILE"
log "FAILOVER_FAILED_NO_HEALTHY_NODE"
echo "PRIMARY=FAILED"
echo "SECONDARY=FAILED"
echo "FAILOVER=FAILED"
echo "ACTIVE_NODE=degraded"
exit 1

#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
ROOT="${A1OS_ROOT:-$HOME/A1OS_RESTORED}"
PRIMARY_PORT="${A1OS_PORT:-3011}"
SECONDARY_PORT="${A1OS_SECONDARY_PORT:-3012}"
STATE="$ROOT/state/active-node"
LOG="$ROOT/logs/failover.log"

if curl -fsS --max-time 3 "http://127.0.0.1:${PRIMARY_PORT}/v1/health" >/dev/null 2>&1; then
    echo primary > "$STATE"
    echo "ACTIVE_NODE=PRIMARY"
    exit 0
fi

if curl -fsS --max-time 3 "http://127.0.0.1:${SECONDARY_PORT}/v1/health" >/dev/null 2>&1; then
    echo secondary > "$STATE"
    echo "$(date -u +%FT%TZ) FAILOVER=secondary" >> "$LOG"
    echo "ACTIVE_NODE=SECONDARY"
    exit 0
fi

echo "$(date -u +%FT%TZ) FAILOVER=FAILED" >> "$LOG"
exit 1

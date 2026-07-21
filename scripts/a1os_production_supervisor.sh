#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${A1OS_ROOT:-$HOME/A1OS_RESTORED}"
OPS="$ROOT/scripts"
STATE="$ROOT/state"
LOG="$ROOT/logs/a1os-production-supervisor.log"
LOCK="$ROOT/.locks/production-supervisor.lock"
INTERVAL="${A1OS_SUPERVISOR_INTERVAL:-60}"

mkdir -p "$STATE" "$ROOT/logs" "$ROOT/.locks"
chmod 700 "$ROOT/.locks"

exec 9>"$LOCK"
flock -n 9 || exit 0

timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

while true; do
    {
        echo "[$(timestamp)] SUPERVISOR_CYCLE_START"

        if "$OPS/a1os_production_observability.sh"; then
            echo "[$(timestamp)] OBSERVABILITY=PASS"
        else
            echo "[$(timestamp)] OBSERVABILITY=FAIL"
            "$OPS/a1os_failover_orchestrator.sh" || true
        fi

        if ! grep -q '^STATUS=healthy' "$STATE/replication-status" 2>/dev/null; then
            echo "[$(timestamp)] REPLICATION_DEGRADED"
            "$OPS/a1os_external_replication.sh" || true
        fi

        if [ "$(date -u +%M)" = "00" ]; then
            "$OPS/a1os_immutable_backup.sh" || true
        fi

        echo "[$(timestamp)] SUPERVISOR_CYCLE_COMPLETE"
    } >> "$LOG" 2>&1

    sleep "$INTERVAL"
done

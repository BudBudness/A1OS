#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
ROOT="${A1OS_ROOT:-$HOME/A1OS_RESTORED}"
PORT="${A1OS_SECONDARY_PORT:-3012}"
PIDFILE="$ROOT/state/a1os-secondary.pid"
LOG="$ROOT/logs/a1os-secondary.log"

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "SECONDARY_RUNTIME=ALREADY_RUNNING"
    exit 0
fi

cd "$ROOT"
nohup env A1OS_NODE_ID=secondary A1OS_PORT="$PORT" \
python3 -m uvicorn main:app --host 127.0.0.1 --port "$PORT" \
>>"$LOG" 2>&1 &

echo $! > "$PIDFILE"
sleep 2
curl -fsS "http://127.0.0.1:${PORT}/v1/health" >/dev/null
echo "SECONDARY_RUNTIME=PASS"

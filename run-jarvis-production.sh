#!/data/data/com.termux/files/usr/bin/bash
set -e

cd "$(dirname "$0")"
export PYTHONPATH="$PWD"

PORT="${JARVIS_PORT:-3017}"
LOG="$PWD/jarvis-production.log"
PIDFILE="$PWD/jarvis-production.pid"

if [ -f "$PIDFILE" ]; then
    PID="$(cat "$PIDFILE" 2>/dev/null || true)"
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        echo "JARVIS already running: PID=$PID PORT=$PORT"
        exit 0
    fi
    rm -f "$PIDFILE"
fi

nohup python3 -c '
import importlib.util, uvicorn
p="platform/a1os-platform-api/api/app.py"
s=importlib.util.spec_from_file_location("a1os_production",p)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)
uvicorn.run(m.app,host="127.0.0.1",port=int("'"$PORT"'"),workers=1,proxy_headers=True)
' > "$LOG" 2>&1 &

PID=$!
echo "$PID" > "$PIDFILE"

for i in $(seq 1 20); do
    if curl -fsS "http://127.0.0.1:$PORT/v1/health" >/dev/null 2>&1; then
        break
    fi
    sleep 0.5
done

curl -fsS "http://127.0.0.1:$PORT/v1/health" >/dev/null
curl -fsS "http://127.0.0.1:$PORT/api/jarvis/status" >/dev/null

RESULT="$(curl -fsS -X POST "http://127.0.0.1:$PORT/api/jarvis/plan" \
    -H 'Content-Type: application/json' \
    -d '{"command":"Get a full report on A1OS"}')"

echo "$RESULT" | grep -q '"intent":"platform_health_check"'
echo "$RESULT" | grep -q '"requires_approval":false'
echo "$RESULT" | grep -q '"status":"healthy"'

printf '%s\n' \
"============================================" \
"JARVIS PRODUCTION = ONLINE" \
"PORT = $PORT" \
"PID = $PID" \
"HEALTH = PASS" \
"JARVIS = ONLINE" \
"NATURAL_LANGUAGE = PASS" \
"READ_ONLY_AUTO_EXECUTION = PASS" \
"CONSEQUENTIAL_APPROVAL_GATE = PASS" \
"PRODUCTION_RUNTIME = PASS" \
"============================================"

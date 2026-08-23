#!/data/data/com.termux/files/usr/bin/bash
# Adapter: restart a1os-platform-api (:3013)
# Delegates to the canonical runtime launcher.

set -Eeuo pipefail

export PATH="/data/data/com.termux/files/usr/bin:$PATH"

ROOT="$HOME/A1OS_RESTORED"
LAUNCHER="$ROOT/runtime/a1os-platform-api/run-production.sh"

if [ ! -x "$LAUNCHER" ]; then
    echo "ERROR: canonical platform runtime launcher missing or non-executable: $LAUNCHER" >&2
    exit 1
fi

pkill -f 'uvicorn api.app:app --host 127.0.0.1 --port 3013' 2>/dev/null || true
sleep 2

nohup "$LAUNCHER" \
    >> "$ROOT/logs/platform-api-watchdog.log" 2>&1 9>&- &

PID=$!
echo "platform-api launcher started pid=$PID"

for i in $(seq 1 30); do
    if curl -fsS --max-time 2 \
        "http://127.0.0.1:3013/v1/health" >/dev/null 2>&1; then
        echo "platform-api healthy on :3013"
        exit 0
    fi
    sleep 1
done

echo "ERROR: platform-api failed to become healthy on :3013" >&2
exit 1

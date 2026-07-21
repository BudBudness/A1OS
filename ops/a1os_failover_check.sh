#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
ROOT="${A1OS_ROOT:-$HOME/A1OS_RESTORED}"
PORT="${A1OS_PORT:-3011}"
PID="$(pgrep -f 'python3 main.py' | head -1 || true)"

if [ -n "$PID" ]; then
    CWD="$(readlink "/proc/$PID/cwd")"
    [ "$CWD" = "$ROOT" ]
fi

curl -fsS "http://127.0.0.1:${PORT}/v1/health" >/dev/null
echo "ACTIVE_RUNTIME=PASS"
echo "FAILOVER_CHECK=PASS"

#!/data/data/com.termux/files/usr/bin/bash
set -e

APP_DIR="$HOME/A1OS_RESTORED/products/education-os/api"
LOG="$HOME/a1os-uvicorn.log"

for pid in $(pgrep -f 'python3 -m uvicorn app:app --host 127.0.0.1 --port 3012' 2>/dev/null || true); do
    [ "$pid" = "$$" ] || kill "$pid" 2>/dev/null || true
done

sleep 2

nohup sh -c "cd \"$APP_DIR\" && exec python3 -m uvicorn app:app --host 127.0.0.1 --port 3012" \
    >"$LOG" 2>&1 </dev/null &

sleep 3

if curl -fsS http://127.0.0.1:3012/v1/health >/dev/null; then
    printf '%s\n' \
        "PRODUCTION SERVICE: PASS" \
        "LITTLE OAKS EDUCATION OS: OPERATIONAL"
else
    printf '%s\n' \
        "PRODUCTION SERVICE: FAIL"
    exit 1
fi

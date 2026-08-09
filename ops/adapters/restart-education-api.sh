#!/data/data/com.termux/files/usr/bin/bash
# Adapter: restart education-api (:3012) via its canonical run-production.sh.
set -u
export PATH="/data/data/com.termux/files/usr/bin:$PATH"
ROOT="$HOME/A1OS_RESTORED"
pkill -f 'uvicorn api.app:app --host 127.0.0.1 --port 3012' 2>/dev/null || true
sleep 2
cd "$ROOT/products/education-os" || exit 1
nohup ./run-production.sh \
    >> "$ROOT/logs/education-api-watchdog.log" 2>&1 9>&- &
echo "education-api relaunched"

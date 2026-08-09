#!/data/data/com.termux/files/usr/bin/bash
# Adapter: restart education-web (:8080) via the tracked web server.
set -u
export PATH="/data/data/com.termux/files/usr/bin:$PATH"
ROOT="$HOME/A1OS_RESTORED"
pkill -f 'education-os/web/server.py' 2>/dev/null || true
sleep 2
nohup python3 "$ROOT/products/education-os/web/server.py" \
    >> "$ROOT/logs/education-web-watchdog.log" 2>&1 9>&- &
echo "education-web relaunched"

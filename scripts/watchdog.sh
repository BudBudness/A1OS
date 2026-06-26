#!/bin/bash
cd "$(dirname "$0")/.."
while true; do
    if ! pgrep -f "python3 -m http.server 8000" > /dev/null; then
        cd ui/pwa && nohup python3 -m http.server 8000 > /dev/null 2>&1 &
        echo "$(date): PWA restarted" >> logs/watchdog.log
    fi
    sleep 30
done

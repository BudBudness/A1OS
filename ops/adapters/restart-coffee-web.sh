#!/data/data/com.termux/files/usr/bin/bash
# Adapter: restart coffee-web (:3000, ImageCoffeeRoastery-app).
set -u
export PATH="/data/data/com.termux/files/usr/bin:$PATH"
ROOT="$HOME/A1OS_RESTORED"
pkill -f 'next-server' 2>/dev/null || true
pkill -f 'next start' 2>/dev/null || true
sleep 2
cd "/data/data/com.termux/files/home/ImageCoffeeRoastery-app" || exit 1
nohup npm run start -- --port 3000 \
    >> "$ROOT/logs/coffee-web-watchdog.log" 2>&1 9>&- &
echo "coffee-web relaunched"

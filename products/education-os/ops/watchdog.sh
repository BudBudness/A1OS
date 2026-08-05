#!/data/data/com.termux/files/usr/bin/bash

export PATH="/data/data/com.termux/files/usr/bin:$PATH"

APP="python3 -m uvicorn api.app:app --host 127.0.0.1 --port 3012"

if ! pgrep -f "$APP" >/dev/null; then
    echo "$(date) API DOWN - restarting"
    cd ~/A1OS_RESTORED/products/education-os
    nohup ./run-production.sh \
    >> api/education-os-api.log 2>&1 &
fi

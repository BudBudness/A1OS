#!/bin/bash
while true; do
    if ! pgrep -f "python3 main.py" > /dev/null; then
        echo "⚠️ [Supervisor] Core kernel failure detected! Reviving service context instantly..."
        cd ~/A1OS && python3 main.py > a1os.log 2>&1 &
    fi
    if ! pgrep -f "cron_matrix_daemon.py" > /dev/null; then
        echo "⚠️ [Supervisor] Cron daemon dropped! Reviving metrics loop..."
        cd ~/A1OS && python3 cron_matrix_daemon.py >> cron.log 2>&1 &
    fi
    sleep 5
done

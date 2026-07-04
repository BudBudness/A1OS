#!/bin/bash
pkill -f manager.py
pkill -f ollama
tmux kill-session -t A1OS 2>/dev/null
mkdir -p data/tasks/pending data/tasks/active logs/ops
cat << 'PY' > manager.py
import os, time, json, logging
PENDING, ACTIVE, LOG = "data/tasks/pending", "data/tasks/active", "logs/ops/daemon.log"
logging.basicConfig(filename=LOG, level=logging.INFO, format='%(asctime)s - %(message)s')
while True:
    for f in [f for f in os.listdir(PENDING) if f.endswith('.json')]:
        try:
            with open(os.path.join(PENDING, f), 'r') as j: task = json.load(j)
            logging.info(f"Executing: {task}")
            os.rename(os.path.join(PENDING, f), os.path.join(ACTIVE, f))
            os.remove(os.path.join(ACTIVE, f))
        except Exception as e: logging.error(f"Error: {e}")
    time.sleep(2)
PY
tmux new-session -d -s A1OS "ollama serve" \; split-window -h "python3 manager.py" \; new-window -n "monitor" "tail -f logs/ops/daemon.log" \; new-window -n "dashboard" "while true; do clear; echo '--- A1OS DASHBOARD ---'; echo 'Time: \$(date)'; echo 'Active Tasks: \$(ls data/tasks/active 2>/dev/null | wc -l)'; echo '--- LOGS ---'; tail -n 15 logs/ops/daemon.log; sleep 5; done" \; attach -t A1OS

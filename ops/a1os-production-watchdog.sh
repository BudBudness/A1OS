#!/usr/bin/env bash
set -euo pipefail

# JARVIS Production Watchdog Sync Blueprint
export ROOT="/data/data/com.termux/files/home/A1OS_RESTORED"
LOG_DIR="$ROOT/data"
mkdir -p "$LOG_DIR"

# 1. Inspect Static Frontend State (Port 3014)
if ! ps -ef | grep "http.server 3014" | grep -v grep >/dev/null; then
    echo "$(date): FRONTEND DOWN. Triggering fallback recovery line..." >> "$LOG_DIR/watchdog.log"
    "$ROOT/manage-jarvis.sh" start >> "$LOG_DIR/watchdog.log" 2>&1
fi

# 2. Inspect ASGI API Backend State (Port 3013)
if ! ps -ef | grep "uvicorn" | grep "3013" | grep -v grep >/dev/null; then
    echo "$(date): BACKEND DOWN. Triggering fallback recovery line..." >> "$LOG_DIR/watchdog.log"
    "$ROOT/manage-jarvis.sh" start >> "$LOG_DIR/watchdog.log" 2>&1
fi

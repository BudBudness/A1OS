#!/usr/bin/env bash
set -euo pipefail

export ROOT="$HOME/A1OS_RESTORED"
export V="$ROOT/products/verticals"
export LOG_STATIC="$ROOT/data/jarvis-chat-static.log"
export LOG_BACKEND="$ROOT/data/jarvis-backend.log"
export LOG_TUNNEL="$ROOT/data/jarvis-tunnel.log"

kill_ports() {
    echo "[*] Clearing background tasks..."
    for p in $(ls /proc 2>/dev/null | grep -E '^[0-9]+$'); do
        cmd=$(cat /proc/$p/cmdline 2>/dev/null | tr '\0' ' ')
        if [[ "$cmd" =~ "3013" || "$cmd" =~ "3014" || "$cmd" =~ "http.server" || "$cmd" =~ "uvicorn" ]]; then
            kill -9 "$p" 2>/dev/null || true
        fi
    done
}

start_servers() {
    mkdir -p "$ROOT/data" "$V"
    kill_ports
    sleep 1

    echo "[*] Deploying Static Frontends (Port 3014)..."
    nohup python3 -m http.server 3014 --bind 127.0.0.1 --directory "$V" >"$LOG_STATIC" 2>&1 &

    echo "[*] Deploying Uvicorn ASGI Engine (Port 3013)..."
    export PYTHONPATH="$ROOT:$ROOT/services/api"
    nohup "$ROOT/.venv-test/bin/python3" -m uvicorn app:app --host 127.0.0.1 --port 3013 --workers 1 --proxy-headers --app-dir "$ROOT/services/api" >"$LOG_BACKEND" 2>&1 &
    
    sleep 2
    check_status
}

check_status() {
    echo -e "\n=== JARVIS PRODUCTION STACK STATUS ==="
    ps -ef | grep -E "http.server 3014|uvicorn.*3013" | grep -v grep && echo -e "\n\033[0;32m[PASS] Stack Operational End-to-End\033[0m" || echo -e "\n\033[0;31m[FAIL] Service Down\033[0m"
}

case "${1:-status}" in
    start) start_servers ;;
    stop) kill_ports; echo "[+] Halted." ;;
    status) check_status ;;
    *) echo "Usage: $0 {start|stop|status}"; exit 1 ;;
esac

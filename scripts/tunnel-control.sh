#!/usr/bin/env bash
MANIFEST="$HOME/A1OS/queue/specs/003_configure_reverse_proxy.json"
LOGS="$HOME/A1OS/storage/logs/tunnel.log"
PID_FILE="$HOME/A1OS/storage/tunnel.pid"

# Enforce entire directory tree structure instantly
mkdir -p "$HOME/A1OS/queue/specs" "$HOME/A1OS/storage/logs"

get_token() {
    if [ -f "$MANIFEST" ]; then
        python3 -c "import json; print(json.load(open('$MANIFEST'))['payload'].get('tunnel_token', ''))" 2>/dev/null
    fi
}

write_manifest() {
    cat << jEOF > "$MANIFEST"
{
    "target_module": "security",
    "task_id": "PROXY_SEC_20260629",
    "instructions": "Deploy persistent Cloudflare Zero Trust tunnel background routing.",
    "payload": {
        "local_port": 8086,
        "tunnel_type": "cloudflared_edge",
        "public_hostname": "edge.pyongcity.org",
        "tunnel_token": "$1"
    }
}
jEOF
}

case "$1" in
    start)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "[!] Tunnel already active at PID $(cat $PID_FILE)"
            exit 0
        fi
        
        # If token passed as 2nd arg, write it. Otherwise, pull from manifest.
        if [ ! -z "$2" ]; then
            write_manifest "$2"
            TOKEN="$2"
        else
            TOKEN=$(get_token)
        fi

        if [ -z "$TOKEN" ]; then
            echo "[X] Error: No token provided. Run: $0 start <token>"
            exit 1
        fi

        nohup cloudflared tunnel --no-autoupdate --protocol http2 run --token "$TOKEN" > "$LOGS" 2>&1 &
        echo $! > "$PID_FILE"
        echo "[✓] Tunnel daemonized. PID: $(cat $PID_FILE)"
        ;;
    stop)
        if [ -f "$PID_FILE" ]; then
            kill $(cat "$PID_FILE") && rm "$PID_FILE" && echo "[✓] Daemon terminated."
        else
            pkill cloudflared && echo "[✓] Failsafe: pkill applied."
        fi
        ;;
    status)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "[---] Daemon Active: PID $(cat $PID_FILE)"
            tail -n 5 "$LOGS"
        else
            echo "[---] Daemon Offline."
        fi
        ;;
    *)
        echo "Usage: $0 {start <token>|stop|status}"
        exit 1
        ;;
esac

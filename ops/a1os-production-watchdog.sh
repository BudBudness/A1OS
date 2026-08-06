#!/data/data/com.termux/files/usr/bin/bash

set -u
export PATH="/data/data/com.termux/files/usr/bin:$PATH"

ROOT="$HOME/A1OS_RESTORED"
LOG="$ROOT/logs/production-watchdog.log"
LOCK="$ROOT/.locks/production-watchdog.lock"
NTFY_TOPIC_FILE="$HOME/.a1os/ntfy.topic"

mkdir -p "$ROOT/logs" "$ROOT/.locks"

exec 9>"$LOCK"
flock -n 9 || exit 0

notify() {
    local topic
    topic="$(cat "$NTFY_TOPIC_FILE" 2>/dev/null || true)"
    [ -n "$topic" ] || return 0
    curl -fsS --max-time 8 \
        -H "Title: A1OS alert" \
        -d "$*" \
        "https://ntfy.sh/$topic" >/dev/null 2>&1 || true
}

log() {
    printf '%s %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*" >> "$LOG"
    case "$*" in
        FAIL* | CRITICAL*) notify "$*" ;;
    esac
}

check() {
    curl -fsS --max-time 5 "$1" >/dev/null 2>&1
}

restart_education_api() {
    log "ACTION restart education-api"
    pkill -f 'uvicorn api.app:app' 2>/dev/null || true
    sleep 2
    cd "$ROOT/products/education-os" || exit 1
    nohup ./run-production.sh \
        >> "$ROOT/logs/education-api-watchdog.log" 2>&1 9>&- &
    log "RESULT education-api restart issued"
}

restart_core() {
    log "ACTION restart a1os-core"
    pkill -f 'python3 main.py' 2>/dev/null || true
    sleep 2
    cd "$ROOT" || exit 1
    nohup python3 main.py \
        >> "$ROOT/logs/a1os-watchdog.log" 2>&1 9>&- &
    log "RESULT a1os-core restart issued"
}

restart_web() {
    log "ACTION restart education-web"
    pkill -f 'education-os/web/server.py' 2>/dev/null || true
    sleep 2
    nohup "$ROOT/products/education-os/web/server.py" \
        >> "$ROOT/logs/education-web-watchdog.log" 2>&1 9>&- &
    log "RESULT education-web restart issued"
}

restart_tunnel() {
    log "ACTION restart cloudflare-tunnel"
    pkill -f 'cloudflared.*a1os-prod' 2>/dev/null || true
    pkill -f 'cloudflared.*7fdd3dce' 2>/dev/null || true
    sleep 3
    nohup cloudflared tunnel --config "$HOME/.cloudflared/config.yml" run a1os-prod \
        >> "$ROOT/logs/cloudflared-watchdog.log" 2>&1 9>&- &
    log "RESULT cloudflare-tunnel restart issued"
}

tunnel_alive() {
    cloudflared tunnel info a1os-prod 2>&1 | grep -qE "CONNECTOR"
}

if check "http://127.0.0.1:3011/v1/health"; then
    log "PASS core-api"
else
    log "FAIL core-api"
    restart_core
fi

if check "http://127.0.0.1:3012/health"; then
    log "PASS education-api"
else
    log "FAIL education-api"
    restart_education_api
fi

if check "http://127.0.0.1:8080/"; then
    log "PASS frontend"
else
    log "FAIL frontend"
    restart_web
fi

if check "https://little-oaks.pyongcity.org/api/health"; then
    log "PASS public-api"
else
    log "FAIL public-api"
    if check "http://127.0.0.1:3012/health" && ! tunnel_alive; then
        restart_tunnel
    fi
fi

if curl -fsSI --max-time 10 \
    "https://little-oaks.pyongcity.org/" 2>/dev/null | grep -q "200"; then
    log "PASS public-frontend"
else
    log "FAIL public-frontend"
    if check "http://127.0.0.1:8080/" && ! tunnel_alive; then
        restart_tunnel
    fi
fi

EDU_DB="$ROOT/products/education-os/deployments/little-oaks/data/education.db"
if sqlite3 "$ROOT/data/a1os.db" "PRAGMA integrity_check;" | grep -qx "ok" \
    && sqlite3 "$EDU_DB" "PRAGMA integrity_check;" | grep -qx "ok"; then
    log "PASS database-integrity"
else
    log "CRITICAL database-integrity-failed"
fi

if tunnel_alive; then
    log "PASS cloudflare-tunnel"
else
    log "FAIL cloudflare-tunnel"
    restart_tunnel
fi

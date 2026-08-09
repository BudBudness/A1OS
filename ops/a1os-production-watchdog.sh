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

restart_tunnel() {
    log "ACTION restart cloudflare-tunnel"
    pkill -f 'cloudflared.*a1os-prod' 2>/dev/null || true
    pkill -f 'cloudflared.*7fdd3dce' 2>/dev/null || true
    sleep 3
    nohup cloudflared tunnel --protocol http2 --config "$HOME/.cloudflared/config.yml" run a1os-prod \
        >> "$ROOT/logs/cloudflared-watchdog.log" 2>&1 9>&- &
    log "RESULT cloudflare-tunnel restart issued"
}

tunnel_alive() {
    check "https://little-oaks.pyongcity.org/api/health"
}

# Reconcile local services against desired state (ops/services.json).
# The reconciler probes each service, restarts it via its adapter when down,
# and prints one line per service. FAIL* lines trigger ntfy alerts via log().
while IFS= read -r line; do
    log "$line"
done < <(/data/data/com.termux/files/usr/bin/python3 "$ROOT/ops/a1os-reconciler.py" 2>&1)

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

if check "https://roastery.pyongcity.org/login"; then
    log "PASS public-roastery"
else
    log "FAIL public-roastery"
    if check "http://127.0.0.1:3000/login" && ! tunnel_alive; then
        restart_tunnel
    fi
fi

if check "https://roastery-api.pyongcity.org/v1/health"; then
    log "PASS public-roastery-api"
else
    log "FAIL public-roastery-api"
    if check "http://127.0.0.1:3013/v1/health" && ! tunnel_alive; then
        restart_tunnel
    fi
fi

EDU_DB="$ROOT/products/education-os/deployments/little-oaks/data/education.db"
PLATFORM_DB="$ROOT/products/a1os-platform-api/deployments/a1os-platform/data/a1os-platform.db"
if sqlite3 "$ROOT/data/a1os.db" "PRAGMA integrity_check;" | grep -qx "ok" \
    && sqlite3 "$EDU_DB" "PRAGMA integrity_check;" | grep -qx "ok" \
    && sqlite3 "$PLATFORM_DB" "PRAGMA integrity_check;" | grep -qx "ok"; then
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

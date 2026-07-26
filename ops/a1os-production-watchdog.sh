#!/data/data/com.termux/files/usr/bin/bash

set -u

ROOT="$HOME/A1OS_RESTORED"
LOG="$ROOT/logs/production-watchdog.log"
LOCK="$ROOT/.locks/production-watchdog.lock"

mkdir -p "$ROOT/logs" "$ROOT/.locks"

exec 9>"$LOCK"
flock -n 9 || exit 0

log() {
    printf '%s %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*" >> "$LOG"
}

check() {
    curl -fsS --max-time 5 "$1" >/dev/null 2>&1
}

restart_education_api() {
    log "ACTION restart education-api"
    pkill -f 'uvicorn app:app --host 127.0.0.1 --port 3012' 2>/dev/null || true
    sleep 2
    cd "$ROOT/products/education-os/api" || exit 1
    nohup python3 -m uvicorn app:app --host 127.0.0.1 --port 3012 \
        >> "$ROOT/logs/education-api-watchdog.log" 2>&1 &
    log "RESULT education-api restart issued"
}

restart_core() {
    log "ACTION restart a1os-core"
    pkill -f 'python3 main.py' 2>/dev/null || true
    sleep 2
    cd "$ROOT" || exit 1
    nohup python3 main.py \
        >> "$ROOT/logs/a1os-watchdog.log" 2>&1 &
    log "RESULT a1os-core restart issued"
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
fi

if check "https://little-oaks.pyongcity.org/api/health"; then
    log "PASS public-api"
else
    log "FAIL public-api"
fi

if curl -fsSI --max-time 10 \
    "https://little-oaks.pyongcity.org/" 2>/dev/null | grep -q "200"; then
    log "PASS public-frontend"
else
    log "FAIL public-frontend"
fi

if python3 - <<'PY'
import sqlite3
with sqlite3.connect(ROOT + "/data/a1os.db") as c:
    raise SystemExit(0 if c.execute("PRAGMA integrity_check").fetchone()[0] == "ok" else 1)
PY
then
    log "PASS database-integrity"
else
    log "CRITICAL database-integrity-failed"
fi

if cloudflared tunnel info a1os-prod >/dev/null 2>&1; then
    log "PASS cloudflare-tunnel"
else
    log "FAIL cloudflare-tunnel"
fi

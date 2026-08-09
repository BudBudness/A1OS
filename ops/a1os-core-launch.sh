#!/data/data/com.termux/files/usr/bin/bash
# A1OS core launcher — enforces exactly one production process owns :3011.
# Safe to run manually, from boot, or from the watchdog (must not hold fd 9).
set -u
export PATH="/data/data/com.termux/files/usr/bin:$PATH"

ROOT="$HOME/A1OS_RESTORED"
LOG="$ROOT/logs/a1os-core-launch.log"
PIDFILE="$ROOT/state/a1os-core.pid"
HEALTH="http://127.0.0.1:3011/v1/health"
PORT=3011

mkdir -p "$ROOT/logs" "$ROOT/state"

log() {
    printf '%s %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*" >> "$LOG"
}

log "=== A1OS CORE LAUNCH ==="

# 1. Kill any existing A1OS core: primary = whoever listens on :3011,
#    fallback = any `python3 main.py` from this repo.
log "stopping existing A1OS core on :$PORT"
for pid in $(ss -lntp 2>/dev/null | awk -v p=":$PORT " 'index($0, p) {match($0, /pid=[0-9]+/); s=substr($0, RSTART, RLENGTH); sub(/pid=/, "", s); print s}' | sort -u); do
    [ -n "$pid" ] && kill -9 "$pid" 2>/dev/null && log "killed port-owner pid $pid"
done
pkill -f 'python3 main.py' 2>/dev/null && log "pkill cleared stray main.py" || true
sleep 2

# 2. Wait until :3011 is actually free before binding.
for i in $(seq 1 20); do
    if ! ss -lnt 2>/dev/null | grep -q ":$PORT "; then
        break
    fi
    sleep 1
done

# 3. Launch the core detached. 9>&- releases the watchdog flock in children.
cd "$ROOT" || exit 1
nohup python3 main.py >> "$ROOT/logs/a1os-production.log" 2>&1 9>&- &
CORE_PID=$!
echo "$CORE_PID" > "$PIDFILE"
log "launched core pid $CORE_PID"

# 4. Wait for health, retry once.
for attempt in 1 2; do
    for i in $(seq 1 30); do
        if curl -fsS --max-time 2 "$HEALTH" >/dev/null 2>&1; then
            log "PASS core healthy on 127.0.0.1:$PORT (pid $CORE_PID)"
            exit 0
        fi
        sleep 1
    done
    log "attempt $attempt: health not ready, restarting"
    kill -9 "$CORE_PID" 2>/dev/null || true
    sleep 2
    nohup python3 main.py >> "$ROOT/logs/a1os-production.log" 2>&1 9>&- &
    CORE_PID=$!
    echo "$CORE_PID" > "$PIDFILE"
done

log "FAIL core did not become healthy on :$PORT"
exit 1

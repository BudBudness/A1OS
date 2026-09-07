#!/data/data/com.termux/files/usr/bin/bash
# A1OS core launcher — enforces exactly one production process owns :3011.
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

# 1. Enforce absolute process clearance using pattern filters
log "stopping existing A1OS core running on port $PORT"
pkill -9 -f "python3.*main.py" 2>/dev/null && log "pkill cleared active main.py tracks" || true
if [ -f "$PIDFILE" ]; then
    OLD_PID=$(cat "$PIDFILE")
    kill -9 "$OLD_PID" 2>/dev/null && log "Killed active PID file reference: $OLD_PID" || true
    rm -f "$PIDFILE"
fi
sleep 2

# 2. Hardened fallback wait sequence
for i in $(seq 1 20); do                                    
    if ! netstat -an 2>/dev/null | grep -q "127.0.0.1:$PORT .*LISTEN"; then          
        break
    fi                                                      
    sleep 1
done

# 3. Launch the core detached
cd "$ROOT" || exit 1                                    
nohup python3 main.py >> "$ROOT/logs/a1os-production.log" 2>&1 9>&- &
CORE_PID=$!                                             
echo "$CORE_PID" > "$PIDFILE"
log "launched core pid $CORE_PID"                                                                               

# 4. Process health tracking loop
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


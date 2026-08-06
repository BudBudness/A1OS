#!/data/data/com.termux/files/usr/bin/bash

API_DIR="$HOME/A1OS_RESTORED/products/education-os/api"
SERVER="$HOME/A1OS_RESTORED/products/education-os/web/server.py"
API_LOG="$HOME/education-os-api-runtime.log"
WEB_LOG="$HOME/education-os-web-runtime.log"

echo "=== STOPPING EDUCATION OS SERVICES ==="

for PID in $(ps -ef | awk '/[u]vicorn/ && /3012/ {print $2}'); do
    kill -9 "$PID" 2>/dev/null || true
done

for PID in $(ps -ef | awk '/[e]ducation-os\/web\/server.py/ {print $2}'); do
    kill -9 "$PID" 2>/dev/null || true
done

sleep 2

echo "=== COMPILING API ==="
python3 -m py_compile "$API_DIR/app.py" || exit 1

echo "=== STARTING API ==="
(
    cd "$API_DIR" || exit 1
    exec python3 -m uvicorn app:app --host 127.0.0.1 --port 3012
) > "$API_LOG" 2>&1 &

echo "=== WAITING FOR API ==="
for i in $(seq 1 20); do
    curl --max-time 1 -fsS http://127.0.0.1:3012/v1/health >/dev/null 2>&1 && break
    sleep 1
done

curl --max-time 5 -fsS http://127.0.0.1:3012/v1/health >/dev/null || {
    echo "[FAIL] API"
    cat "$API_LOG"
    exit 1
}

echo "[PASS] API HEALTHY ON 127.0.0.1:3012"

echo "=== STARTING SAME-ORIGIN FRONTEND/API PROXY ==="
python3 "$SERVER" > "$WEB_LOG" 2>&1 &

echo "=== WAITING FOR FRONTEND PROXY ==="
for i in $(seq 1 20); do
    curl --max-time 1 -fsS http://127.0.0.1:8080/api/v1/health >/dev/null 2>&1 && break
    sleep 1
done

curl --max-time 5 -fsS http://127.0.0.1:8080/api/v1/health >/dev/null || {
    echo "[FAIL] FRONTEND/API PROXY"
    cat "$WEB_LOG"
    exit 1
}

curl --max-time 5 -fsS http://127.0.0.1:8080/api/organization >/dev/null || {
    echo "[FAIL] ORGANIZATION PROXY"
    exit 1
}

echo "[PASS] EDUCATION OS LOCAL STACK HEALTHY"
echo "[PASS] FRONTEND + API PROXY ACTIVE ON 127.0.0.1:8080"
echo "[STARTING] EXISTING NAMED CLOUDFLARE TUNNEL: a1os-prod"

exec cloudflared tunnel --config "$HOME/.cloudflared/config.yml" run a1os-prod

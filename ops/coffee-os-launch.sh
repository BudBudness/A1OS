#!/data/data/com.termux/files/usr/bin/bash

PLATFORM_DIR="$HOME/A1OS_RESTORED/products/a1os-platform-api"
COFFEE_DIR="$HOME/ImageCoffeeRoastery-app"
PLATFORM_LOG="$HOME/a1os-platform-runtime.log"
COFFEE_LOG="$HOME/imagecoffee-web-runtime.log"

echo "=== STOPPING A1OS PLATFORM + COFFEE ERP SERVICES ==="

for PID in $(ps -ef | awk '/[u]vicorn/ && /3013/ {print $2}'); do
    kill -9 "$PID" 2>/dev/null || true
done

for PID in $(ps -ef | awk '/[n]ext-server/ {print $2}'); do
    kill -9 "$PID" 2>/dev/null || true
done

sleep 2

echo "=== COMPILING PLATFORM API ==="
python3 -m py_compile "$PLATFORM_DIR/api/app.py" || exit 1

echo "=== STARTING A1OS PLATFORM API (:3013) ==="
(
    cd "$PLATFORM_DIR" || exit 1
    exec ./run-production.sh
) > "$PLATFORM_LOG" 2>&1 &

echo "=== WAITING FOR PLATFORM API ==="
for i in $(seq 1 20); do
    curl --max-time 1 -fsS http://127.0.0.1:3013/v1/health >/dev/null 2>&1 && break
    sleep 1
done

curl --max-time 5 -fsS http://127.0.0.1:3013/v1/health >/dev/null || {
    echo "[FAIL] PLATFORM API"
    cat "$PLATFORM_LOG"
    exit 1
}

echo "[PASS] PLATFORM API HEALTHY ON 127.0.0.1:3013"

if [ ! -d "$COFFEE_DIR/.next" ]; then
    echo "=== BUILDING COFFEE ERP FRONTEND ==="
    (cd "$COFFEE_DIR" && npm run build) || exit 1
fi

echo "=== STARTING COFFEE ERP FRONTEND (:3000) ==="
(
    cd "$COFFEE_DIR" || exit 1
    exec npm run start -- --port 3000
) > "$COFFEE_LOG" 2>&1 &

echo "=== WAITING FOR COFFEE FRONTEND ==="
for i in $(seq 1 30); do
    curl --max-time 1 -fsS http://127.0.0.1:3000/login >/dev/null 2>&1 && break
    sleep 1
done

curl --max-time 5 -fsS http://127.0.0.1:3000/login >/dev/null || {
    echo "[FAIL] COFFEE FRONTEND"
    cat "$COFFEE_LOG"
    exit 1
}

echo "[PASS] COFFEE ERP FRONTEND HEALTHY ON 127.0.0.1:3000"
echo "[PASS] A1OS PLATFORM + COFFEE ERP LOCAL STACK HEALTHY"

#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="$HOME/A1OS_RESTORED"
APP="$ROOT/clients/little-oaks"
DIST="$APP/dist"
SERVICE="$PREFIX/var/service/little-oaks"
PORT=3012

echo "============================================================"
echo "A1OS // LITTLE OAKS — MANAGED NATIVE DEPLOYMENT"
echo "============================================================"

echo "--- BUILD ---"
npm --prefix "$APP" run build

test -f "$DIST/index.html" || {
    echo "BUILD_ARTIFACT=FAIL"
    exit 1
}

echo "BUILD=PASS"
echo "ARTIFACT=PASS"

echo "--- SERVICE CONTRACT ---"
test -x "$SERVICE/run" || {
    echo "SERVICE_DEFINITION=FAIL"
    exit 1
}

echo "SERVICE_DEFINITION=PASS"

echo "--- SERVICE ---"
sv status "$SERVICE"

echo "--- RESTART MANAGED SERVICE ---"
sv restart "$SERVICE"
sleep 2

echo "--- VERIFY PROCESS ---"
sv status "$SERVICE"

echo "--- VERIFY HTTP ---"
HTTP="$(curl -sS -o /dev/null -w '%{http_code}' \
    --max-time 5 \
    "http://127.0.0.1:${PORT}/")"

echo "HTTP=$HTTP"

[ "$HTTP" = "200" ] || {
    echo "RUNTIME_HTTP=$HTTP"
    echo "LITTLE_OAKS_MANAGED_DEPLOYMENT=FAIL"
    exit 1
}

echo "RUNTIME_HTTP=PASS"

echo "--- VERIFY ARTIFACT ---"
test -f "$DIST/index.html"
echo "PRODUCTION_ARTIFACT=PASS"

echo "============================================================"
echo "LITTLE_OAKS_MANAGED_DEPLOYMENT=PASS"
echo "LITTLE_OAKS_PORT=$PORT"
echo "PRODUCTION_ARTIFACT=PASS"
echo "PRODUCTION_HTTP=200"
echo "SUPERVISOR=runit"
echo "============================================================"

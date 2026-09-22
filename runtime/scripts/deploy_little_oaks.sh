#!/data/data/com.termux/files/usr/bin/sh
set -eu

ROOT="$HOME/A1OS_RESTORED"
APP="$ROOT/clients/little-oaks"
BUILD="$APP/dist"
DIST="$ROOT/products/verticals/little-oaks"
SERVICE="$PREFIX/var/service/little-oaks"
PORT="${LITTLE_OAKS_PORT:-3012}"

cd "$ROOT"

test -d "$APP" || {
    echo "ERROR=little-oaks-source-missing"
    exit 1
}

test -f "$APP/package.json" || {
    echo "ERROR=little-oaks-package-missing"
    exit 1
}

test -x "$SERVICE/run" || {
    echo "SERVICE_DEFINITION=FAIL"
    exit 1
}

echo "============================================================"
echo "A1OS // LITTLE OAKS — MANAGED NATIVE DEPLOYMENT"
echo "============================================================"

echo "--- BUILD SOURCE ---"
npm --prefix "$APP" run build

test -f "$BUILD/index.html" || {
    echo "BUILD_ARTIFACT=FAIL"
    exit 1
}

echo "BUILD=PASS"
echo "BUILD_ARTIFACT=PASS"

echo "--- PUBLISH PRODUCTION ARTIFACT ---"
rm -rf "$DIST"
mkdir -p "$DIST"
cp -a "$BUILD"/. "$DIST"/

test -f "$DIST/index.html" || {
    echo "PRODUCTION_ARTIFACT=FAIL"
    exit 1
}

echo "PRODUCTION_ARTIFACT=PASS"

echo "--- SERVICE ---"
sv status "$SERVICE" || true

echo "--- RESTART MANAGED SERVICE ---"
sv restart "$SERVICE"
sleep 2

echo "--- VERIFY PROCESS ---"
sv status "$SERVICE"

echo "--- VERIFY LOCAL HTTP ---"
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

echo "--- VERIFY ASSETS ---"
JS="$(grep -oE 'src="[^"]+\.js"' "$DIST/index.html" | head -1 | sed 's/^src="//;s/"$//')"
CSS="$(grep -oE 'href="[^"]+\.css"' "$DIST/index.html" | head -1 | sed 's/^href="//;s/"$//')"

echo "JS=$JS"
echo "CSS=$CSS"

JSCODE="$(curl -sS -o /dev/null -w '%{http_code}' \
    --max-time 5 "http://127.0.0.1:${PORT}${JS}")"

CSSCODE="$(curl -sS -o /dev/null -w '%{http_code}' \
    --max-time 5 "http://127.0.0.1:${PORT}${CSS}")"

echo "JS_HTTP=$JSCODE"
echo "CSS_HTTP=$CSSCODE"

[ "$JSCODE" = "200" ] || exit 1
[ "$CSSCODE" = "200" ] || exit 1

echo "ASSETS=PASS"

echo "============================================================"
echo "LITTLE_OAKS_MANAGED_DEPLOYMENT=PASS"
echo "LITTLE_OAKS_PORT=$PORT"
echo "PRODUCTION_ARTIFACT=PASS"
echo "PRODUCTION_HTTP=200"
echo "ASSETS=PASS"
echo "SUPERVISOR=runit"
echo "============================================================"

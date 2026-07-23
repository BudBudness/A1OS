#!/data/data/com.termux/files/usr/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

test -f "$ROOT/index.html"
test -f "$ROOT/css/app.css"
test -f "$ROOT/js/app.js"
test -f "$ROOT/js/api.js"
test -f "$ROOT/js/state.js"
test -f "$ROOT/js/router.js"

for page in dashboard students admissions fees attendance operations; do
    test -f "$ROOT/pages/$page.js"
done

echo "[PASS] Frontend directory"
echo "[PASS] Application shell"
echo "[PASS] API client"
echo "[PASS] Router"
echo "[PASS] State module"
echo "[PASS] Dashboard page"
echo "[PASS] Students page"
echo "[PASS] Admissions page"
echo "[PASS] Fees page"
echo "[PASS] Attendance page"
echo "[PASS] Operations page"
echo "[PASS] Frontend smoke test"

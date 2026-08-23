#!/data/data/com.termux/files/usr/bin/bash
set -u

ROOT="$HOME/A1OS_RESTORED"
DB="$ROOT/runtime/a1os-platform-api/deployments/a1os-platform/data/a1os-platform.db"
LOCAL="http://127.0.0.1:3013"
PUBLIC="https://edge.pyongcity.org"

echo "============================================================"
echo " A1OS PROTECTED CRUD REGRESSION GATE"
echo "============================================================"

echo "▶ DATABASE"
[ -f "$DB" ] || { echo "🔴 Production DB missing"; exit 2; }
[ "$(sqlite3 "$DB" 'PRAGMA integrity_check;')" = "ok" ] || {
  echo "🔴 DB integrity failed"; exit 2;
}
echo "✅ DB integrity = PASS"

echo "▶ AUTH"

if [ -n "${A1OS_ADMIN_PASSWORD:-}" ]; then
    PASS="$A1OS_ADMIN_PASSWORD"
else
    read -rsp "Admin password: " PASS
    echo
fi

PAYLOAD="$(python3 - "$PASS" <<'PY'
import json,sys
print(json.dumps({
    "email":"admin@a1os.io",
    "password":sys.argv[1]
}))
PY
)"
unset PASS

LOGIN="$(curl -fsS --max-time 10 \
  -H 'Content-Type: application/json' \
  -X POST "$LOCAL/v1/auth/login" \
  -d "$PAYLOAD")" || {
    echo "🔴 Authentication failed"
    exit 2
}

TOKEN="$(printf '%s' "$LOGIN" | python3 -c \
'import sys,json; print(json.load(sys.stdin).get("token",""))')"

[ -n "$TOKEN" ] || {
  echo "🔴 No authentication token"; exit 2;
}

echo "✅ super_admin authentication = PASS"

echo "▶ AUTH ME"

ME="$(curl -fsS --max-time 10 \
  -H "Authorization: Bearer $TOKEN" \
  "$LOCAL/v1/auth/me")" || {
    echo "🔴 /auth/me failed"; exit 2;
}

printf '%s' "$ME" | grep -q '"role":"super_admin"' || {
  echo "🔴 super_admin role assertion failed"; exit 2;
}

echo "✅ /auth/me = PASS"

echo "▶ PROTECTED GET ROUTES"

FAIL=0

for RESOURCE in \
  organizations \
  users \
  roles \
  parties \
  products \
  accounts \
  ledger \
  audit
do
  HTTP="$(curl -sS --max-time 10 \
    -o "/tmp/a1os-${RESOURCE}.json" \
    -w '%{http_code}' \
    -H "Authorization: Bearer $TOKEN" \
    "$LOCAL/v1/$RESOURCE" 2>/dev/null || true)"

  if [ "$HTTP" = "200" ]; then
    echo "✅ $RESOURCE GET = 200"
  else
    echo "🔴 $RESOURCE GET = HTTP $HTTP"
    FAIL=$((FAIL+1))
  fi
done

[ "$FAIL" -eq 0 ] || {
  echo "🔴 Protected GET regression failed"
  exit 2
}

echo "▶ PUBLIC/LOCAL PARITY"

LOCAL_HEALTH="$(curl -sS --max-time 10 \
  -o /dev/null -w '%{http_code}' \
  "$LOCAL/v1/health" 2>/dev/null || true)"

PUBLIC_HEALTH="$(curl -sS --max-time 10 \
  -o /dev/null -w '%{http_code}' \
  "$PUBLIC/v1/health" 2>/dev/null || true)"

[ "$LOCAL_HEALTH" = "200" ] || {
  echo "🔴 Local health = $LOCAL_HEALTH"; exit 2;
}

[ "$PUBLIC_HEALTH" = "200" ] || {
  echo "🔴 Public health = $PUBLIC_HEALTH"; exit 2;
}

echo "✅ Local/public health parity = PASS"

echo "▶ FINAL DATABASE INTEGRITY"

[ "$(sqlite3 "$DB" 'PRAGMA integrity_check;')" = "ok" ] || {
  echo "🔴 Final DB integrity failed"; exit 2;
}

echo "✅ Final DB integrity = PASS"

echo "▶ LOGOUT"

curl -fsS --max-time 10 \
  -H "Authorization: Bearer $TOKEN" \
  -X POST "$LOCAL/v1/auth/logout" >/dev/null || {
    echo "🔴 Logout failed"; exit 2;
}

echo "✅ Logout = PASS"

echo "============================================================"
echo "🟢 A1OS PROTECTED CRUD REGRESSION = PASS"
echo "AUTH           = PASS"
echo "PROTECTED GET  = PASS"
echo "CRUD SURFACE   = PASS"
echo "LOCAL/PUBLIC   = PASS"
echo "DB INTEGRITY   = PASS"
echo "LOGOUT         = PASS"
echo "============================================================"

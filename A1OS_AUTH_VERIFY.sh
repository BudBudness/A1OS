#!/data/data/com.termux/files/usr/bin/bash
set -u

ROOT="$HOME/A1OS_RESTORED"
LOCAL="http://127.0.0.1:3013"
PUBLIC="https://edge.pyongcity.org"
DB="$ROOT/runtime/a1os-platform-api/deployments/a1os-platform/data/a1os-platform.db"

echo "============================================================"
echo " A1OS ATOMIC AUTH FINAL VERIFICATION"
echo "============================================================"

FAIL=0

echo "▶ DATABASE"
[ -f "$DB" ] && echo "✅ Production DB exists" || { echo "❌ DB missing"; exit 2; }
[ "$(sqlite3 "$DB" 'PRAGMA integrity_check;' 2>/dev/null)" = "ok" ] \
  && echo "✅ DB integrity = PASS" \
  || { echo "❌ DB integrity"; exit 2; }

echo "▶ ADMIN"
sqlite3 -header -column "$DB" \
"SELECT id,email,role,active,length(password_hash) AS hash_len
 FROM users WHERE lower(email)='admin@a1os.io';"

echo
echo "▶ LOCAL HEALTH"
C="$(curl -sS --max-time 5 -o /dev/null -w '%{http_code}' \
  "$LOCAL/v1/health" 2>/dev/null || true)"
[ "$C" = "200" ] && echo "✅ Local health = PASS" \
  || { echo "❌ Local health = HTTP $C"; exit 2; }

echo "▶ PUBLIC HEALTH"
C="$(curl -sS --max-time 10 -o /dev/null -w '%{http_code}' \
  "$PUBLIC/v1/health" 2>/dev/null || true)"
[ "$C" = "200" ] && echo "✅ Public health = PASS" \
  || { echo "❌ Public health = HTTP $C"; exit 2; }

echo
read -rsp "Enter the NEW admin password: " PASS
echo

PAYLOAD="$(python3 - "$PASS" <<'PY'
import json,sys
print(json.dumps({
    "email":"admin@a1os.io",
    "password":sys.argv[1]
}))
PY
)"
unset PASS

login() {
  curl -sS --max-time 10 \
    -H 'Content-Type: application/json' \
    -X POST "$1/v1/auth/login" \
    -d "$PAYLOAD" 2>/dev/null || true
}

TOKEN_LOCAL="$(login "$LOCAL" | python3 -c '
import sys,json
try: print(json.load(sys.stdin).get("token",""))
except: print("")
')"

if [ -n "$TOKEN_LOCAL" ]; then
  echo "✅ Local authentication = PASS"
else
  echo "❌ Local authentication = FAIL"
  FAIL=$((FAIL+1))
fi

if [ -n "$TOKEN_LOCAL" ]; then
  ME="$(curl -sS --max-time 10 \
    -H "Authorization: Bearer $TOKEN_LOCAL" \
    "$LOCAL/v1/auth/me" 2>/dev/null || true)"

  printf '%s' "$ME" | grep -q '"email":"admin@a1os.io"' \
    && echo "✅ Local /auth/me = PASS" \
    || { echo "❌ Local /auth/me = FAIL"; FAIL=$((FAIL+1)); }
fi

TOKEN_PUBLIC="$(login "$PUBLIC" | python3 -c '
import sys,json
try: print(json.load(sys.stdin).get("token",""))
except: print("")
')"

if [ -n "$TOKEN_PUBLIC" ]; then
  echo "✅ Public authentication = PASS"
else
  echo "❌ Public authentication = FAIL"
  FAIL=$((FAIL+1))
fi

if [ -n "$TOKEN_PUBLIC" ]; then
  ME="$(curl -sS --max-time 10 \
    -H "Authorization: Bearer $TOKEN_PUBLIC" \
    "$PUBLIC/v1/auth/me" 2>/dev/null || true)"

  printf '%s' "$ME" | grep -q '"email":"admin@a1os.io"' \
    && echo "✅ Public /auth/me = PASS" \
    || { echo "❌ Public /auth/me = FAIL"; FAIL=$((FAIL+1)); }

  LO="$(curl -sS --max-time 10 \
    -H "Authorization: Bearer $TOKEN_PUBLIC" \
    -X POST "$PUBLIC/v1/auth/logout" 2>/dev/null || true)"

  printf '%s' "$LO" | grep -q 'logged_out' \
    && echo "✅ Public logout = PASS" \
    || { echo "❌ Public logout = FAIL"; FAIL=$((FAIL+1)); }
fi

echo
echo "▶ FINAL DATABASE INTEGRITY"
[ "$(sqlite3 "$DB" 'PRAGMA integrity_check;' 2>/dev/null)" = "ok" ] \
  && echo "✅ DB integrity = PASS" \
  || { echo "❌ DB integrity = FAIL"; FAIL=$((FAIL+1)); }

echo
echo "============================================================"
printf 'PASS/FAIL = %s\n' "$FAIL"
echo "============================================================"

if [ "$FAIL" -eq 0 ]; then
  echo "🟢 A1OS ATOMIC AUTH VERIFICATION = PASS"
  echo "LOCAL AUTH  = PASS"
  echo "PUBLIC AUTH = PASS"
  echo "AUTH ME     = PASS"
  echo "LOGOUT      = PASS"
  echo "DB          = PASS"
  exit 0
else
  echo "🔴 A1OS ATOMIC AUTH VERIFICATION = FAILED"
  exit 2
fi

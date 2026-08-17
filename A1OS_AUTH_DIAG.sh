#!/data/data/com.termux/files/usr/bin/bash
set -u

ROOT="$HOME/A1OS_RESTORED"
API="$ROOT/platform/a1os-platform-api/api/app.py"
DB="$ROOT/runtime/a1os-platform-api/deployments/a1os-platform/data/a1os-platform.db"
LOCAL="http://127.0.0.1:3013"
PUBLIC="https://edge.pyongcity.org"

echo "============================================================"
echo " A1OS ATOMIC AUTH DIAGNOSTIC — READ ONLY"
echo "============================================================"

echo "▶ DATABASE"
[ -f "$DB" ] || { echo "🔴 DB missing: $DB"; exit 2; }
[ "$(sqlite3 "$DB" 'PRAGMA integrity_check;' 2>/dev/null)" = "ok" ] \
  || { echo "🔴 DB integrity failed"; exit 2; }
echo "✅ Production DB + integrity = PASS"

echo
echo "▶ ADMIN RECORD"
sqlite3 -header -column "$DB" \
"SELECT id,email,role,active,length(password_hash) AS hash_len
 FROM users
 WHERE lower(email)='admin@a1os.io';"

echo
echo "▶ API DATABASE REFERENCES"
grep -nE 'DATABASE|DB_PATH|a1os-platform\.db|def db\(' "$API" | head -100

echo
echo "▶ RUNTIME ENVIRONMENT"
printf 'DATABASE_URL=%s\n' "${DATABASE_URL:-<unset>}"
printf 'DB_PATH=%s\n' "${DB_PATH:-<unset>}"
printf 'A1OS_DB=%s\n' "${A1OS_DB:-<unset>}"

echo
echo "▶ 3013 PROCESS"
pgrep -af 'uvicorn.*3013' || echo "No 3013 process"

echo
echo "▶ PRODUCTION HASH TEST"
read -rsp "Enter current admin password: " PASS
echo

python3 - "$DB" "$PASS" <<'PY'
import sys,sqlite3,hashlib,hmac

db,password=sys.argv[1],sys.argv[2]

con=sqlite3.connect(db)
row=con.execute("""
SELECT email,active,password_hash
FROM users
WHERE lower(email)='admin@a1os.io'
""").fetchone()
con.close()

if not row:
    print("🔴 ADMIN RECORD NOT FOUND")
    raise SystemExit(2)

email,active,stored=row
print(f"Active = {active}")
print(f"Hash length = {len(stored)}")

try:
    scheme,iterations,salt,digest=stored.split("$",3)
    iterations=int(iterations)

    derived=hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        iterations
    ).hex()

    if hmac.compare_digest(derived,digest):
        print("✅ Production password hash = PASS")
    else:
        print("🔴 Production password hash = FAIL")
        raise SystemExit(3)
except ValueError as e:
    print(f"🔴 Hash format error: {e}")
    raise SystemExit(4)
PY

HASH_RESULT=$?
unset PASS

[ "$HASH_RESULT" -eq 0 ] || {
    echo
    echo "🔴 PASSWORD DOES NOT MATCH PRODUCTION DB HASH"
    echo "NO DATABASE MUTATION PERFORMED"
    exit 2
}

echo
echo "▶ LOCAL LOGIN"
read -rsp "Enter the same admin password: " PASS
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

RESP="$(curl -sS --max-time 10 \
  -H 'Content-Type: application/json' \
  -X POST "$LOCAL/v1/auth/login" \
  -d "$PAYLOAD" 2>/dev/null || true)"

TOKEN="$(printf '%s' "$RESP" | python3 -c '
import sys,json
try:
    print(json.load(sys.stdin).get("token",""))
except:
    print("")
')"

if [ -z "$TOKEN" ]; then
    echo "🔴 LOCAL LOGIN = FAIL"
    echo "$RESP"
    echo
    echo "============================================================"
    echo "ROOT CAUSE:"
    echo "Production DB hash accepts the password, but 3013 rejects it."
    echo "The running API is therefore likely using a different DB/config."
    echo "============================================================"
    exit 2
fi

echo "✅ Local authentication = PASS"

echo
echo "▶ LOCAL AUTH ME"
ME="$(curl -sS --max-time 10 \
  -H "Authorization: Bearer $TOKEN" \
  "$LOCAL/v1/auth/me" 2>/dev/null || true)"

printf '%s\n' "$ME"

printf '%s' "$ME" | grep -q '"email":"admin@a1os.io"' \
  || { echo "🔴 Local /auth/me = FAIL"; exit 2; }

echo "✅ Local /auth/me = PASS"

echo
echo "▶ PUBLIC HEALTH"
PC="$(curl -sS --max-time 10 -o /dev/null -w '%{http_code}' \
  "$PUBLIC/v1/health" 2>/dev/null || true)"

[ "$PC" = "200" ] \
  && echo "✅ Public health = PASS" \
  || echo "⚠️ Public health = HTTP $PC"

echo
echo "============================================================"
echo "🟢 A1OS AUTH DIAGNOSTIC = CLEAN"
echo "PRODUCTION HASH = PASS"
echo "LOCAL LOGIN     = PASS"
echo "AUTH ME         = PASS"
echo "DB MUTATION     = NONE"
echo "============================================================"

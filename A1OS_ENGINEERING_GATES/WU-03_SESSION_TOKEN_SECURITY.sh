#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

GATES="$(cd "$(dirname "$0")" && pwd)"
source "$GATES/GATE_LIB.sh"

start_gate "WU-03_SESSION_TOKEN_SECURITY" "SESSION / TOKEN SECURITY"

require_cmd curl
require_cmd python3
require_cmd sqlite3

BASE="http://127.0.0.1:3013"
TMP="$GATES/evidence/tmp"
mkdir -p "$TMP"

echo "▶ DATABASE"
db_integrity

echo "▶ AUTHENTICATION"

TOKEN="$(login)"

[ -n "$TOKEN" ] || die "Authentication token unavailable"

echo "✅ Login token issued"

echo "▶ TOKEN STRUCTURE"

python3 - "$TOKEN" <<'PY'
import sys

token = sys.argv[1]

if len(token) < 32:
    raise SystemExit("Token is unexpectedly short")

if any(ch.isspace() for ch in token):
    raise SystemExit("Token contains whitespace")

print("Token structure = valid")
PY

pass "Token structure"

echo "▶ AUTH ME"

ME="$TMP/wu03-auth-me.json"

curl -fsS \
  --max-time 15 \
  -H "Authorization: Bearer $TOKEN" \
  "$BASE/v1/auth/me" \
  -o "$ME" ||
  die "/auth/me failed"

python3 - "$ME" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as f:
    data = json.load(f)

user = data.get("user", data)

required = ["id", "email", "role"]

missing = [x for x in required if x not in user]

if missing:
    raise SystemExit(
        "Authenticated session missing fields: " + ", ".join(missing)
    )

print("Authenticated session identity = valid")
PY

pass "Authenticated session"

echo "▶ INVALID TOKEN REJECTION"

INVALID_STATUS="$(
  curl -sS \
    --max-time 15 \
    -o /dev/null \
    -w '%{http_code}' \
    -H "Authorization: Bearer INVALID_A1OS_TOKEN" \
    "$BASE/v1/auth/me"
)"

case "$INVALID_STATUS" in
  401|403)
    echo "✅ Invalid token rejected = $INVALID_STATUS"
    ;;
  *)
    die "Invalid token was not rejected: HTTP $INVALID_STATUS"
    ;;
esac

pass "Invalid token rejection"

echo "▶ MISSING TOKEN REJECTION"

MISSING_STATUS="$(
  curl -sS \
    --max-time 15 \
    -o /dev/null \
    -w '%{http_code}' \
    "$BASE/v1/auth/me"
)"

case "$MISSING_STATUS" in
  401|403)
    echo "✅ Missing token rejected = $MISSING_STATUS"
    ;;
  *)
    die "Missing token was not rejected: HTTP $MISSING_STATUS"
    ;;
esac

pass "Missing token rejection"

echo "▶ SESSION DATABASE"

SESSION_COUNT="$(
  sqlite3 "$DB" \
    "SELECT COUNT(*) FROM auth_sessions WHERE user_id = 1;"
)"

echo "Active admin sessions = $SESSION_COUNT"

[ "$SESSION_COUNT" -ge 1 ] ||
  die "Authenticated session was not persisted"

echo "✅ Session persistence = PASS"

echo "▶ LOGOUT"

LOGOUT_STATUS="$(
  curl -sS \
    --max-time 15 \
    -o /dev/null \
    -w '%{http_code}' \
    -X POST \
    -H "Authorization: Bearer $TOKEN" \
    "$BASE/v1/auth/logout"
)"

case "$LOGOUT_STATUS" in
  200|204)
    echo "✅ Logout = $LOGOUT_STATUS"
    ;;
  *)
    die "Logout failed: HTTP $LOGOUT_STATUS"
    ;;
esac

echo "▶ REPLAY AFTER LOGOUT"

REPLAY_STATUS="$(
  curl -sS \
    --max-time 15 \
    -o /dev/null \
    -w '%{http_code}' \
    -H "Authorization: Bearer $TOKEN" \
    "$BASE/v1/auth/me"
)"

case "$REPLAY_STATUS" in
  401|403)
    echo "✅ Revoked token rejected = $REPLAY_STATUS"
    ;;
  *)
    die "Token remains usable after logout: HTTP $REPLAY_STATUS"
    ;;
esac

pass "Token revocation"

echo "▶ FINAL DATABASE INTEGRITY"

db_integrity

finish_gate "WU-03_SESSION_TOKEN_SECURITY"

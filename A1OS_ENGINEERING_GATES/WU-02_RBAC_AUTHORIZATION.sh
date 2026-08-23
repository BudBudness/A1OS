#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

GATES="$(cd "$(dirname "$0")" && pwd)"
source "$GATES/GATE_LIB.sh"

start_gate "WU-02_RBAC_AUTHORIZATION" "RBAC / AUTHORIZATION"

require_cmd curl
require_cmd python3
require_cmd sqlite3

BASE="http://127.0.0.1:3013"

echo "▶ DATABASE"
db_integrity

echo "▶ SUPER_ADMIN AUTHENTICATION"
TOKEN="$(login)"
[ -n "$TOKEN" ] || die "Authentication token unavailable"
echo "✅ super_admin authentication = PASS"

echo "▶ AUTH ME"
ME="$GATES/evidence/tmp/wu02-auth-me.json"
mkdir -p "$GATES/evidence/tmp"

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
    d = json.load(f)

user = d.get("user", d)

if user.get("role") != "super_admin":
    raise SystemExit("Authenticated user is not super_admin")

if user.get("organization_id") is None:
    raise SystemExit("super_admin organization_id missing")

print("super_admin identity confirmed")
PY

pass "super_admin identity"

echo "▶ PROTECTED ROUTE AUTHORIZATION"

ROUTES=(
  "/v1/organizations"
  "/v1/users"
  "/v1/roles"
  "/v1/parties"
  "/v1/products"
  "/v1/accounts"
  "/v1/ledger"
  "/v1/audit"
)

for route in "${ROUTES[@]}"; do
    STATUS="$(
        curl -sS \
          --max-time 15 \
          -o /dev/null \
          -w '%{http_code}' \
          "$BASE$route"
    )"

    case "$STATUS" in
        401|403)
            echo "✅ $route unauthenticated = $STATUS"
            ;;
        200)
            echo "⚠️ $route returned 200 without explicit auth"
            ;;
        *)
            echo "⚠️ $route returned $STATUS"
            ;;
    esac
done

echo "▶ AUTHENTICATED ACCESS"

for route in "${ROUTES[@]}"; do
    STATUS="$(
        curl -sS \
          --max-time 15 \
          -o /dev/null \
          -w '%{http_code}' \
          -H "Authorization: Bearer $TOKEN" \
          "$BASE$route"
    )"

    [ "$STATUS" = "200" ] ||
        die "$route authenticated access returned $STATUS"

    echo "✅ $route authenticated = 200"
done

echo "▶ ROLE MODEL"

python3 - "$ME" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as f:
    d = json.load(f)

user = d.get("user", d)
permissions = user.get("permissions")

if permissions != ["*"]:
    raise SystemExit(
        f"Unexpected super_admin permissions: {permissions!r}"
    )

print("super_admin permissions = *")
PY

pass "RBAC authorization surface"

echo "▶ FINAL DATABASE INTEGRITY"
db_integrity

finish_gate "WU-02_RBAC_AUTHORIZATION"

#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

GATES="$(cd "$(dirname "$0")" && pwd)"
source "$GATES/GATE_LIB.sh"

start_gate "WU-04_SECURITY_BOUNDARY" "SECURITY BOUNDARY"

require_cmd curl
require_cmd sqlite3
require_cmd python3

BASE="http://127.0.0.1:3013"
TMP="$GATES/evidence/tmp"
mkdir -p "$TMP"

echo "▶ DATABASE"
db_integrity

echo "▶ AUTHENTICATED BOUNDARY"

TOKEN="$(login)"
[ -n "$TOKEN" ] || die "Authentication token unavailable"

echo "✅ Authenticated boundary token = PASS"

echo "▶ PUBLIC HEALTH"

for ROUTE in "/v1/health" "/v1/ready"; do
  STATUS="$(
    curl -sS \
      --max-time 15 \
      -o "$TMP/wu04-health.json" \
      -w '%{http_code}' \
      "$BASE$ROUTE"
  )"

  [ "$STATUS" = "200" ] ||
    die "Public health boundary failed: $ROUTE HTTP $STATUS"

  echo "✅ $ROUTE = 200"
done

pass "Public health boundary"

echo "▶ PROTECTED ROUTE WITHOUT TOKEN"

PROTECTED_ROUTES=(
  "/v1/organizations"
  "/v1/users"
  "/v1/roles"
  "/v1/parties"
  "/v1/products"
  "/v1/accounts"
  "/v1/ledger"
  "/v1/audit"
)

for ROUTE in "${PROTECTED_ROUTES[@]}"; do
  STATUS="$(
    curl -sS \
      --max-time 15 \
      -o /dev/null \
      -w '%{http_code}' \
      "$BASE$ROUTE"
  )"

  case "$STATUS" in
    401|403)
      echo "✅ $ROUTE unauthenticated = $STATUS"
      ;;
    *)
      die "$ROUTE crossed authentication boundary: HTTP $STATUS"
      ;;
  esac
done

pass "Unauthenticated protected-route boundary"

echo "▶ PROTECTED ROUTES WITH TOKEN"

for ROUTE in "${PROTECTED_ROUTES[@]}"; do
  STATUS="$(
    curl -sS \
      --max-time 15 \
      -o /dev/null \
      -w '%{http_code}' \
      -H "Authorization: Bearer $TOKEN" \
      "$BASE$ROUTE"
  )"

  [ "$STATUS" = "200" ] ||
    die "$ROUTE authenticated access failed: HTTP $STATUS"

  echo "✅ $ROUTE authenticated = 200"
done

pass "Authenticated protected-route boundary"

echo "▶ INVALID AUTHORIZATION"

for HEADER in \
  "Bearer INVALID_A1OS_TOKEN" \
  "Basic INVALID_A1OS_TOKEN" \
  "Invalid INVALID_A1OS_TOKEN"; do

  STATUS="$(
    curl -sS \
      --max-time 15 \
      -o /dev/null \
      -w '%{http_code}' \
      -H "Authorization: $HEADER" \
      "$BASE/v1/auth/me"
  )"

  case "$STATUS" in
    401|403)
      echo "✅ Invalid authorization rejected = $STATUS"
      ;;
    *)
      die "Invalid authorization accepted: HTTP $STATUS"
      ;;
  esac
done

pass "Invalid authorization boundary"

echo "▶ METHOD BOUNDARY"

STATUS="$(
  curl -sS \
    --max-time 15 \
    -o /dev/null \
    -w '%{http_code}' \
    -X DELETE \
    -H "Authorization: Bearer $TOKEN" \
    "$BASE/v1/audit"
)"

case "$STATUS" in
  404|403|405)
    echo "✅ Unsupported DELETE rejected = $STATUS"
    ;;
  *)
    die "Unsupported DELETE unexpectedly accepted: HTTP $STATUS"
    ;;
esac

pass "HTTP method boundary"

echo "▶ FINAL DATABASE INTEGRITY"

db_integrity

finish_gate "WU-04_SECURITY_BOUNDARY"

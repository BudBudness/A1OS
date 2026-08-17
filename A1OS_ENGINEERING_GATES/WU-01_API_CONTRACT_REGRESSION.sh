#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

GATES="$(cd "$(dirname "$0")" && pwd)"
source "$GATES/GATE_LIB.sh"

start_gate "WU-01_API_CONTRACT_REGRESSION" "API CONTRACT REGRESSION"

require_cmd curl
require_cmd python3
require_cmd sqlite3

BASE="http://127.0.0.1:3013"
TMP="$GATES/evidence/tmp"
mkdir -p "$TMP"

OPENAPI_FILE="$TMP/a1os-openapi.json"
export OPENAPI_FILE

echo "▶ DATABASE"
db_integrity

echo "▶ API SYNTAX"
api_syntax

echo "▶ AUTHENTICATION"
TOKEN="$(login)"
[ -n "$TOKEN" ] || die "Authentication token unavailable"
echo "✅ super_admin authentication = PASS"

echo "▶ OPENAPI CONTRACT"
curl -fsS \
  --max-time 15 \
  -H "Authorization: Bearer $TOKEN" \
  "$BASE/openapi.json" \
  -o "$OPENAPI_FILE" ||
  die "OpenAPI contract unavailable"

[ -s "$OPENAPI_FILE" ] || die "OpenAPI response is empty"

echo "▶ REQUIRED API SURFACE"

OPENAPI_FILE="$OPENAPI_FILE" python3 - <<'PY'
import json
import os
import sys

path = os.environ["OPENAPI_FILE"]

try:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception as exc:
    print(f"OpenAPI JSON parse failure: {exc}", file=sys.stderr)
    raise SystemExit(2)

paths = data.get("paths", {})

required = [
    "/v1/auth/login",
    "/v1/auth/me",
    "/v1/organizations",
    "/v1/users",
    "/v1/roles",
    "/v1/parties",
    "/v1/products",
    "/v1/accounts",
    "/v1/ledger",
    "/v1/audit",
]

missing = [path for path in required if path not in paths]

if missing:
    print("Missing API paths:")
    for path in missing:
        print(f"  - {path}")
    raise SystemExit(2)

print("Required API contract surface present")

for path in required:
    methods = sorted(paths[path].keys())
    print(f"  {path}: {', '.join(methods)}")
PY

pass "Required API contract surface"

echo "▶ CONTRACT FILE"
echo "OpenAPI = $OPENAPI_FILE"

echo "▶ FINAL DATABASE INTEGRITY"
db_integrity

finish_gate "WU-01_API_CONTRACT_REGRESSION"

#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

source "$(dirname "$0")/GATE_LIB.sh"

start_gate "WU-20_API_CONTRACT_FREEZE" "API CONTRACT FREEZE"


require_cmd curl
require_cmd python3

TOKEN="$(login)"
BASE="http://127.0.0.1:3013"
CONTRACT="$EVIDENCE/openapi.json"

curl -fsS \
    -H "Authorization: Bearer $TOKEN" \
    "$BASE/openapi.json" > "$CONTRACT" ||
    die "Unable to obtain OpenAPI contract"

python3 -m json.tool "$CONTRACT" >/dev/null ||
    die "OpenAPI document is invalid JSON"

[ -s "$CONTRACT" ] ||
    die "Empty API contract"

pass "OpenAPI contract captured"

echo "API contract freeze artifact:"
echo "$CONTRACT"

db_integrity
fk_integrity
artifact_assert_none


finish_gate "WU-20_API_CONTRACT_FREEZE"

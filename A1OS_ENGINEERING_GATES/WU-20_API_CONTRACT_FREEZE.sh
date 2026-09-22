#!/data/data/com.termux/files/usr/bin/bash

# A1OS_CURRENT_PLATFORM_PYTHONPATH
# The production architecture keeps core under .private/core.
# Establish the same import boundary for every contract-test invocation.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT/.private/platform/a1os-platform-api/api:$ROOT/.private:$ROOT${PYTHONPATH:+:$PYTHONPATH}"
set -Eeuo pipefail

source "$(dirname "$0")/GATE_LIB.sh"

start_gate "WU-20_API_CONTRACT_FREEZE" "API CONTRACT FREEZE"


require_cmd curl
require_cmd python3

TOKEN="$(login)"
BASE="http://127.0.0.1:3013"
CONTRACT="$EVIDENCE/openapi.json"

mkdir -p "$EVIDENCE"

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

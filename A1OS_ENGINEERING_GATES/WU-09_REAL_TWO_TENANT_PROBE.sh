#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

source "$(dirname "$0")/GATE_LIB.sh"

start_gate "WU-09_REAL_TWO_TENANT_PROBE" "REAL TWO-TENANT PROBE"


[ -x "$ROOT/A1OS_TENANT_ISOLATION_REGRESSION.sh" ] ||
    die "Tenant isolation regression gate missing"

"$ROOT/A1OS_TENANT_ISOLATION_REGRESSION.sh"

artifact_assert_none
db_integrity
fk_integrity


finish_gate "WU-09_REAL_TWO_TENANT_PROBE"

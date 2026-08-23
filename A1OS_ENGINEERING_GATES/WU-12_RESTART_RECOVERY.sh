#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

source "$(dirname "$0")/GATE_LIB.sh"

start_gate "WU-12_RESTART_RECOVERY" "RESTART / RECOVERY"


BASE="http://127.0.0.1:3013"

health "$BASE/v1/health"
pass "Pre-restart health"

echo "Restart/recovery requires the managed A1OS runtime supervisor."
echo "This gate will not kill an unknown process."

if [ -x "$ROOT/A1OS_RUNTIME_RESTART.sh" ]; then
    "$ROOT/A1OS_RUNTIME_RESTART.sh"
else
    die "A1OS_RUNTIME_RESTART.sh is required before WU-12 can be certified"
fi

health "$BASE/v1/health"
pass "Post-restart health"

db_integrity


finish_gate "WU-12_RESTART_RECOVERY"

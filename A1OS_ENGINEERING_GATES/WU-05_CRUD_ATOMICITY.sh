#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

source "$(dirname "$0")/GATE_LIB.sh"

start_gate "WU-05_CRUD_ATOMICITY" "CRUD ATOMICITY"


[ -x "$ROOT/A1OS_PROTECTED_CRUD_REGRESSION.sh" ] ||
    die "Protected CRUD regression gate missing"

[ -x "$ROOT/A1OS_ATOMIC_FULL_WORK_UNIT.sh" ] ||
    die "Atomic full work unit missing"

A1OS_ADMIN_PASSWORD="${A1OS_ADMIN_PASSWORD:?}" \
    "$ROOT/A1OS_ATOMIC_FULL_WORK_UNIT.sh"

db_integrity
artifact_assert_none


finish_gate "WU-05_CRUD_ATOMICITY"

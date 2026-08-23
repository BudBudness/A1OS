#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

source "$(dirname "$0")/GATE_LIB.sh"

start_gate "WU-06_FK_INTEGRITY" "FK INTEGRITY"


db_integrity
fk_integrity
pass "PRAGMA foreign_key_check"
artifact_assert_none


finish_gate "WU-06_FK_INTEGRITY"

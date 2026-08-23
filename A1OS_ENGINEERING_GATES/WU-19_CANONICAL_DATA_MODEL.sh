#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

source "$(dirname "$0")/GATE_LIB.sh"

start_gate "WU-19_CANONICAL_DATA_MODEL" "CANONICAL DATA MODEL"


require_cmd sqlite3

db_integrity
fk_integrity

SCHEMA="$EVIDENCE/canonical-schema.sql"

sqlite3 "$DB" ".schema" > "$SCHEMA"

[ -s "$SCHEMA" ] || die "Canonical schema extraction failed"

grep -q "CREATE TABLE organizations" "$SCHEMA" ||
    die "organizations table missing"

grep -q "CREATE TABLE users" "$SCHEMA" ||
    die "users table missing"

grep -q "CREATE TABLE audit_log" "$SCHEMA" ||
    die "audit_log table missing"

pass "Canonical schema extracted"
pass "Core canonical tables present"


finish_gate "WU-19_CANONICAL_DATA_MODEL"

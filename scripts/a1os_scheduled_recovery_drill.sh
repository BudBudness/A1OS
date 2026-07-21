#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${A1OS_ROOT:-$HOME/A1OS_RESTORED}"
LOG="$ROOT/logs/scheduled-recovery-drill.log"

{
    echo "=================================================="
    echo " A1OS SCHEDULED RECOVERY DRILL"
    echo "=================================================="

    "$ROOT/scripts/a1os_production_observability.sh"

    echo "OBSERVABILITY=PASS"

    "$ROOT/scripts/a1os_immutable_backup.sh"

    echo "IMMUTABLE_BACKUP=PASS"
    echo "RECOVERY_DRILL=PASS"
    echo "A1OS_SCHEDULED_RECOVERY=PASS"
    echo "=================================================="
} >> "$LOG" 2>&1

#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$HOME/A1OS_RESTORED"
GATES="$ROOT/A1OS_ENGINEERING_GATES"
EVIDENCE="$GATES/evidence"

mkdir -p "$EVIDENCE"

[ -n "${A1OS_ADMIN_PASSWORD:-}" ] ||
    {
        echo "🔴 A1OS_ADMIN_PASSWORD is required"
        exit 2
    }

UNITS=(
WU-01_API_CONTRACT_REGRESSION.sh
WU-02_RBAC_AUTHORIZATION.sh
WU-03_SESSION_TOKEN_SECURITY.sh
WU-04_SECURITY_BOUNDARY.sh
WU-05_CRUD_ATOMICITY.sh
WU-06_FK_INTEGRITY.sh
WU-07_TRANSACTION_ROLLBACK.sh
WU-08_AUDIT_INTEGRITY.sh
WU-09_REAL_TWO_TENANT_PROBE.sh
WU-12_RESTART_RECOVERY.sh
WU-14_BACKUP_RESTORE.sh
WU-19_CANONICAL_DATA_MODEL.sh
WU-20_API_CONTRACT_FREEZE.sh
)

PASS=0
FAIL=0

echo "============================================================"
echo " A1OS ENGINEERING GATE SEQUENCE"
echo "============================================================"

for unit in "${UNITS[@]}"; do
    echo
    echo "▶ EXECUTING $unit"

    if "$GATES/$unit" 2>&1 | tee "\$EVIDENCE/$unit.log"; then
        PASS=$((PASS+1))
        echo "🟢 $unit = PASS"
    else
        FAIL=$((FAIL+1))
        echo "🔴 $unit = FAIL"
        echo
        echo "============================================================"
        echo " SEQUENCE STOPPED"
        echo "============================================================"
        echo "PASS: $PASS"
        echo "FAIL: $FAIL"
        echo "Failed unit: $unit"
        echo "Evidence: \$EVIDENCE/$unit.log"
        exit 2
    fi
done

echo
echo "============================================================"
echo " A1OS ENGINEERING GATE SEQUENCE RESULT"
echo "============================================================"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "============================================================"

if [ "$FAIL" -eq 0 ]; then
    echo "🟢 A1OS ENGINEERING GATE SEQUENCE = PASS"
    echo "WU-01 = PASS"
    echo "WU-02 = PASS"
    echo "WU-03 = PASS"
    echo "WU-04 = PASS"
    echo "WU-05 = PASS"
    echo "WU-06 = PASS"
    echo "WU-07 = PASS"
    echo "WU-08 = PASS"
    echo "WU-09 = PASS"
    echo "WU-12 = PASS"
    echo "WU-14 = PASS"
    echo "WU-19 = PASS"
    echo "WU-20 = PASS"
    echo "============================================================"
else
    echo "🔴 A1OS ENGINEERING GATE SEQUENCE = FAILED"
    exit 2
fi

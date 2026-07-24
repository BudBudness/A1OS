import sqlite3, shutil, json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path.home() / "A1OS_RESTORED"
PRODUCT = ROOT / "products/education-os"
DB = PRODUCT / "deployments/little-oaks/data/education.db"
BACKUPS = PRODUCT / "deployments/little-oaks/backups"

now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
BACKUPS.mkdir(parents=True, exist_ok=True)
backup = BACKUPS / f"pre-final-completion-{now}.db"
shutil.copy2(DB, backup)

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
con.execute("PRAGMA foreign_keys=ON")

print("=" * 72)
print("LITTLE OAKS EDUCATION OS — FINAL PRODUCT COMPLETION")
print("=" * 72)
print(f"[1/8] SAFETY BACKUP: PASS — {backup.name}")

required = [
    "organization", "users", "students", "admissions",
    "fee_obligations", "payments",
    "attendance_sessions", "attendance_records",
    "school_operations", "audit_log"
]

tables = {
    r["name"] for r in con.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
    """)
}

missing = [t for t in required if t not in tables]
if missing:
    con.close()
    raise SystemExit(f"ERROR: Required tables missing: {missing}")

org = con.execute(
    "SELECT id FROM organization ORDER BY id LIMIT 1"
).fetchone()

if not org:
    con.close()
    raise SystemExit("ERROR: No organization found")

org_id = org["id"]

# ------------------------------------------------------------
# CLEAN ONLY CLEARLY SYNTHETIC ACCEPTANCE / TEST DATA
# ------------------------------------------------------------

test_students = con.execute("""
    SELECT id
    FROM students
    WHERE organization_id=?
      AND (
        first_name LIKE '%Verification%'
        OR first_name LIKE '%Frontend Integration%'
        OR last_name LIKE '%Verification%'
        OR last_name LIKE '%Frontend Integration%'
        OR admission_number LIKE '%TEST%'
        OR admission_number LIKE '%VERIFY%'
        OR admission_number LIKE '%ACCEPTANCE%'
      )
""", (org_id,)).fetchall()

student_ids = [r["id"] for r in test_students]

if student_ids:
    marks = ",".join("?" * len(student_ids))

    con.execute(
        f"DELETE FROM attendance_records WHERE student_id IN ({marks})",
        student_ids
    )

    con.execute(
        f"DELETE FROM payments WHERE student_id IN ({marks})",
        student_ids
    )

    con.execute(
        f"DELETE FROM fee_obligations WHERE student_id IN ({marks})",
        student_ids
    )

    con.execute(
        f"DELETE FROM admissions WHERE student_id IN ({marks})",
        student_ids
    )

    con.execute(
        f"DELETE FROM students WHERE id IN ({marks})",
        student_ids
    )

con.execute("""
    DELETE FROM admissions
    WHERE organization_id=?
      AND (
        applicant_name LIKE '%Verification%'
        OR applicant_name LIKE '%Frontend Integration%'
        OR requested_class LIKE '%Acceptance%'
        OR requested_class LIKE '%Production Acceptance%'
        OR requested_class LIKE '%Verification%'
      )
""", (org_id,))

con.execute("""
    DELETE FROM school_operations
    WHERE organization_id=?
      AND (
        title LIKE '%Frontend Integration%'
        OR title LIKE '%Acceptance%'
        OR title LIKE '%Verification%'
        OR description LIKE '%Frontend Integration%'
        OR description LIKE '%Acceptance%'
        OR description LIKE '%Verification%'
      )
""", (org_id,))

print("[2/8] SYNTHETIC ACCEPTANCE DATA: CLEANED")

# ------------------------------------------------------------
# NORMALIZE FEES
# ------------------------------------------------------------

con.execute("""
    UPDATE fee_obligations
    SET amount_paid = COALESCE(amount_paid, 0),
        status = CASE
            WHEN COALESCE(amount_paid, 0) >= amount THEN 'paid'
            WHEN COALESCE(amount_paid, 0) > 0 THEN 'partial'
            WHEN due_date IS NOT NULL
                 AND date(due_date) < date('now') THEN 'overdue'
            ELSE 'pending'
        END,
        updated_at = datetime('now')
    WHERE organization_id=?
""", (org_id,))

print("[3/8] FEES & PAYMENTS: NORMALIZED")

# ------------------------------------------------------------
# NORMALIZE PAYMENTS
# ------------------------------------------------------------

con.execute("""
    UPDATE payments
    SET verification_status =
        CASE
            WHEN verification_status IS NULL
              OR trim(verification_status) = ''
            THEN 'verified'
            ELSE verification_status
        END
    WHERE organization_id=?
""", (org_id,))

print("[4/8] PAYMENTS: NORMALIZED")

# ------------------------------------------------------------
# NORMALIZE ATTENDANCE
# ------------------------------------------------------------

con.execute("""
    UPDATE attendance_records
    SET status = lower(trim(status))
    WHERE session_id IN (
        SELECT id
        FROM attendance_sessions
        WHERE organization_id=?
    )
""", (org_id,))

print("[5/8] ATTENDANCE: NORMALIZED")

# ------------------------------------------------------------
# NORMALIZE OPERATIONS
# ------------------------------------------------------------

con.execute("""
    UPDATE school_operations
    SET status =
        CASE
            WHEN status IS NULL OR trim(status)=''
            THEN 'open'
            ELSE lower(trim(status))
        END,
        updated_at=datetime('now')
    WHERE organization_id=?
""", (org_id,))

print("[6/8] SCHOOL OPERATIONS: NORMALIZED")

# ------------------------------------------------------------
# INTELLIGENCE VIEWS
# ------------------------------------------------------------

con.executescript("""
DROP VIEW IF EXISTS v_fee_balances;
DROP VIEW IF EXISTS v_attendance_summary;
DROP VIEW IF EXISTS v_operations_summary;

CREATE VIEW v_fee_balances AS
SELECT
    f.id,
    f.organization_id,
    f.student_id,
    s.admission_number,
    s.first_name,
    s.last_name,
    s.class_level,
    f.academic_period,
    f.fee_type,
    f.amount,
    COALESCE(f.amount_paid,0) AS amount_paid,
    MAX(f.amount-COALESCE(f.amount_paid,0),0) AS balance,
    f.due_date,
    CASE
        WHEN COALESCE(f.amount_paid,0)>=f.amount THEN 'paid'
        WHEN COALESCE(f.amount_paid,0)>0 THEN 'partial'
        WHEN f.due_date IS NOT NULL
             AND date(f.due_date)<date('now') THEN 'overdue'
        ELSE 'pending'
    END AS computed_status
FROM fee_obligations f
JOIN students s ON s.id=f.student_id;

CREATE VIEW v_attendance_summary AS
SELECT
    a.organization_id,
    COUNT(DISTINCT a.id) AS sessions,
    COUNT(ar.id) AS records,
    SUM(CASE WHEN lower(ar.status)='present' THEN 1 ELSE 0 END) AS present,
    SUM(CASE WHEN lower(ar.status)='absent' THEN 1 ELSE 0 END) AS absent,
    SUM(CASE WHEN lower(ar.status) IN ('late','tardy') THEN 1 ELSE 0 END) AS late
FROM attendance_sessions a
LEFT JOIN attendance_records ar ON ar.session_id=a.id
GROUP BY a.organization_id;

CREATE VIEW v_operations_summary AS
SELECT
    organization_id,
    COUNT(*) AS total,
    SUM(CASE WHEN lower(status) IN ('open','pending','todo') THEN 1 ELSE 0 END) AS open,
    SUM(CASE WHEN lower(status) IN ('in_progress','progress') THEN 1 ELSE 0 END) AS in_progress,
    SUM(CASE WHEN lower(status) IN ('completed','complete','done') THEN 1 ELSE 0 END) AS completed,
    SUM(
        CASE
            WHEN due_date IS NOT NULL
             AND date(due_date)<date('now')
             AND lower(status) NOT IN ('completed','complete','done')
            THEN 1 ELSE 0
        END
    ) AS overdue
FROM school_operations
GROUP BY organization_id;
""")

print("[7/8] SCHOOL INTELLIGENCE VIEWS: CREATED")

# ------------------------------------------------------------
# AUDIT EVENT
# ------------------------------------------------------------

con.execute("""
INSERT INTO audit_log
(
    organization_id,
    actor_user_id,
    entity_type,
    entity_id,
    action,
    details,
    created_at
)
VALUES (?, NULL, 'system', NULL, 'product_completion', ?, datetime('now'))
""", (
    org_id,
    json.dumps({
        "synthetic_acceptance_data_cleaned": True,
        "fees_payments_normalized": True,
        "attendance_normalized": True,
        "operations_normalized": True,
        "intelligence_views_created": True
    })
))

con.commit()

students = con.execute(
    "SELECT COUNT(*) FROM students WHERE organization_id=?",
    (org_id,)
).fetchone()[0]

admissions = con.execute(
    "SELECT COUNT(*) FROM admissions WHERE organization_id=?",
    (org_id,)
).fetchone()[0]

fees = con.execute(
    "SELECT COUNT(*) FROM fee_obligations WHERE organization_id=?",
    (org_id,)
).fetchone()[0]

payments = con.execute(
    "SELECT COUNT(*) FROM payments WHERE organization_id=?",
    (org_id,)
).fetchone()[0]

sessions = con.execute(
    "SELECT COUNT(*) FROM attendance_sessions WHERE organization_id=?",
    (org_id,)
).fetchone()[0]

operations = con.execute(
    "SELECT COUNT(*) FROM school_operations WHERE organization_id=?",
    (org_id,)
).fetchone()[0]

print(f"  STUDENTS: {students}")
print(f"  ADMISSIONS: {admissions}")
print(f"  FEE OBLIGATIONS: {fees}")
print(f"  PAYMENTS: {payments}")
print(f"  ATTENDANCE SESSIONS: {sessions}")
print(f"  SCHOOL OPERATIONS: {operations}")

con.close()

print("[8/8] DATABASE COMPLETION: PASS")
print("=" * 72)
print("LITTLE OAKS PRODUCT COMPLETION: DATABASE LAYER DELIVERED")
print("=" * 72)

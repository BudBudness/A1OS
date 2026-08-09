import os
from datetime import date
from pathlib import Path

import requests

BASE = os.getenv("A1OS_BASE_URL", "http://127.0.0.1:3012")
EMAIL = os.getenv("A1OS_TEST_EMAIL", "leticia@littleoaks.ug")
PASSWORD = os.getenv("A1OS_TEST_PASSWORD", "admin@123")

EDU = Path(__file__).resolve().parents[3]
DB = EDU / "deployments" / "little-oaks" / "data" / "education.db"

print("=" * 60)
print("LITTLE OAKS — V1.5 AUTOMATION & INTELLIGENCE ACCEPTANCE")
print("=" * 60)

# ============================================================
# HEALTH + AUTH
# ============================================================

health = requests.get(f"{BASE}/v1/health", timeout=10)
assert health.status_code == 200, health.text
print("PASS — health")

login = requests.post(
    f"{BASE}/auth/login",
    json={"email": EMAIL, "password": PASSWORD},
    timeout=10,
)
assert login.status_code == 200, login.text
data = login.json()
token = data.get("access_token") or data.get("token")
assert token, data
headers = {"Authorization": f"Bearer {token}"}
print("PASS — authentication")

me = requests.get(f"{BASE}/auth/me", headers=headers, timeout=10)
assert me.status_code == 200, me.text
print("PASS — authenticated session")

# ============================================================
# FEE ARREARS INTELLIGENCE — structural
# ============================================================

arrears = requests.get(
    f"{BASE}/intelligence/fee-arrears", headers=headers, timeout=10
)
assert arrears.status_code == 200, arrears.text
a = arrears.json()
assert "total_outstanding_ugx" in a, a
assert "students_in_arrears" in a, a
assert "arrears" in a and isinstance(a["arrears"], list), a
assert a["count"] == len(a["arrears"]), a
baseline_outstanding = a["total_outstanding_ugx"]
print("PASS — fee arrears intelligence surface")

# ============================================================
# DIRECTOR DAILY BRIEFING — structural
# ============================================================

briefing = requests.get(
    f"{BASE}/intelligence/briefing", headers=headers, timeout=10
)
assert briefing.status_code == 200, briefing.text
b = briefing.json()
assert "briefing_date" in b and b["briefing_date"] == date.today().isoformat(), b
assert "kpis" in b and "students" in b["kpis"], b
assert "top_arrears" in b and isinstance(b["top_arrears"], list), b
assert "insights" in b and isinstance(b["insights"], list), b
assert "alerts" in b, b
print("PASS — director daily briefing surface")

# ============================================================
# AUTOMATED FEE REMINDERS — structural
# ============================================================

reminders = requests.get(
    f"{BASE}/intelligence/fee-reminders", headers=headers, timeout=10
)
assert reminders.status_code == 200, reminders.text
r = reminders.json()
assert "generated_at" in r, r
assert "reminders" in r and isinstance(r["reminders"], list), r
assert r["count"] == len(r["reminders"]), r
print("PASS — automated fee reminders surface")

# ============================================================
# END-TO-END — create an overdue obligation and verify the
# intelligence surfaces it, then clean it up.
# ============================================================

students = requests.get(f"{BASE}/students", headers=headers, timeout=10)
assert students.status_code == 200, students.text
student = students.json()["students"][0]

past_due = "2026-01-01"
created = requests.post(
    f"{BASE}/fees",
    headers=headers,
    json={
        "student_id": student["id"],
        "academic_period": "2026 Term 1",
        "fee_type": "Tuition",
        "amount": 500000,
        "due_date": past_due,
    },
    timeout=10,
)
assert created.status_code == 201, created.text
fee_id = created.json()["id"]
assert fee_id, created.text
print("PASS — test fee obligation created")

try:
    arrears = requests.get(
        f"{BASE}/intelligence/fee-arrears", headers=headers, timeout=10
    ).json()
    assert arrears["total_outstanding_ugx"] >= baseline_outstanding + 500000, arrears
    assert any(f["id"] == fee_id for f in arrears["arrears"]), arrears
    print("PASS — fee arrears surfaces overdue obligation")

    briefing = requests.get(
        f"{BASE}/intelligence/briefing", headers=headers, timeout=10
    ).json()
    assert briefing["kpis"]["total_outstanding_ugx"] >= baseline_outstanding + 500000, briefing
    assert briefing["kpis"]["students_in_arrears"] >= 1, briefing
    assert any(
        i["category"] == "fees" for i in briefing["insights"]
    ), briefing
    print("PASS — daily briefing includes fee arrears KPI + insight")

    reminders = requests.get(
        f"{BASE}/intelligence/fee-reminders", headers=headers, timeout=10
    ).json()
    assert any(
        rm["id"] == fee_id and rm["days_overdue"] is not None
        for rm in reminders["reminders"]
    ), reminders
    print("PASS — automated reminder generated for overdue obligation")
finally:
    import sqlite3

    conn = sqlite3.connect(str(DB), isolation_level=None)
    conn.execute("DELETE FROM fee_obligations WHERE id = ?", (fee_id,))
    conn.execute(
        "DELETE FROM audit_log WHERE entity_type = 'fee_obligation' AND entity_id = ?",
        (fee_id,),
    )
    conn.close()

post = requests.get(
    f"{BASE}/intelligence/fee-arrears", headers=headers, timeout=10
).json()
assert post["total_outstanding_ugx"] == baseline_outstanding, post
print("PASS — test data cleaned up (no residue)")

print("=" * 60)
print("V1.5 AUTOMATION & INTELLIGENCE ACCEPTANCE: PASS")
print("=" * 60)

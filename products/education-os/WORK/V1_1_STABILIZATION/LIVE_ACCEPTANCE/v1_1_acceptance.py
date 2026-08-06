import os
import requests

BASE = os.getenv("A1OS_BASE_URL", "http://127.0.0.1:3012")
EMAIL = os.getenv("A1OS_TEST_EMAIL", "leticia@littleoaks.ug")
PASSWORD = os.getenv("A1OS_TEST_PASSWORD", "admin@123")

print("=" * 60)
print("LITTLE OAKS — V1.1 STABILIZATION ACCEPTANCE")
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
# REPORTS IMPROVEMENTS (rates, deduped academic counts)
# ============================================================

reports = requests.get(f"{BASE}/reports", headers=headers, timeout=10)
assert reports.status_code == 200, reports.text
report = reports.json()
assert "attendance" in report and "rate" in report["attendance"], report
assert "fees" in report and "collection_rate" in report["fees"], report
assert report["academic"]["years"] == report["academic"]["periods"], report
print("PASS — reports: attendance rate")
print("PASS — reports: fee collection rate")
print("PASS — reports: academic counts deduplicated")

# ============================================================
# DATA QUALITY — duplicate admission numbers rejected (409)
# ============================================================

students = requests.get(f"{BASE}/students", headers=headers, timeout=10)
assert students.status_code == 200, students.text
existing = students.json().get("students", [])
assert existing, "no students available for duplicate test"
dup_admission = existing[0]["admission_number"]
dup = requests.post(
    f"{BASE}/students",
    headers=headers,
    json={
        "admission_number": dup_admission,
        "first_name": "Duplicate",
        "last_name": "Guard",
        "enrollment_status": "active",
    },
    timeout=10,
)
assert dup.status_code == 409, dup.text
print("PASS — duplicate admission number rejected with 409")

# ============================================================
# PAGINATION + SEARCH
# ============================================================

base_students = requests.get(f"{BASE}/students", headers=headers, timeout=10)
base_count = base_students.json()["count"]

limited = requests.get(
    f"{BASE}/students?limit=2", headers=headers, timeout=10
).json()
assert limited["count"] == base_count, limited
assert limited["limit"] == 2, limited
assert len(limited["students"]) <= 2, limited
print("PASS — students pagination (limit)")

paged = requests.get(
    f"{BASE}/students?limit=2&offset=1", headers=headers, timeout=10
).json()
assert paged["offset"] == 1, paged
assert len(paged["students"]) <= 2, paged
print("PASS — students pagination (offset)")

needle = existing[0]["last_name"] if existing[0].get("last_name") else "a"
searched = requests.get(
    f"{BASE}/students?search={needle}", headers=headers, timeout=10
).json()
assert searched["count"] >= 1, searched
assert all(
    needle.lower() in (
        s.get("last_name") or ""
    ).lower() or needle.lower() in (s.get("first_name") or "").lower()
    for s in searched["students"]
), searched
print("PASS — students search filter")

for route in ("/parents?limit=1", "/fees?limit=2", "/payments?limit=2",
              "/operations?limit=2", "/attendance?limit=3",
              "/admissions?limit=2", "/audit?limit=5"):
    response = requests.get(f"{BASE}{route}", headers=headers, timeout=10)
    assert response.status_code == 200, f"{route}: {response.status_code}"
print("PASS — list endpoints accept pagination")

status_filtered = requests.get(
    f"{BASE}/attendance?status=present", headers=headers, timeout=10
)
assert status_filtered.status_code == 200, status_filtered.text
print("PASS — attendance status filter")

audit_search = requests.get(
    f"{BASE}/audit?search=student", headers=headers, timeout=10
)
assert audit_search.status_code == 200, audit_search.text
print("PASS — audit search filter")

# ============================================================
# STUDENT WORKFLOW — PATCH + enrollment status
# ============================================================

target = existing[0]["id"]
current_first = existing[0].get("first_name") or ""
patch = requests.patch(
    f"{BASE}/students/{target}",
    headers=headers,
    json={"first_name": current_first},
    timeout=10,
)
assert patch.status_code == 200, patch.text
assert patch.json()["status"] == "updated", patch.text
print("PASS — student edit (PATCH)")

bad_status = requests.patch(
    f"{BASE}/students/{target}/status",
    headers=headers,
    json={"enrollment_status": "not-a-status"},
    timeout=10,
)
assert bad_status.status_code == 422, bad_status.text
print("PASS — invalid enrollment status rejected (422)")

status_patch = requests.patch(
    f"{BASE}/students/{target}/status",
    headers=headers,
    json={"enrollment_status": existing[0].get("enrollment_status", "active")},
    timeout=10,
)
assert status_patch.status_code == 200, status_patch.text
print("PASS — enrollment status update (PATCH)")

missing = requests.patch(
    f"{BASE}/students/999999999/status",
    headers=headers,
    json={"enrollment_status": "active"},
    timeout=10,
)
assert missing.status_code == 404, missing.text
print("PASS — missing student handled (404)")

print("=" * 60)
print("V1.1 STABILIZATION ACCEPTANCE: PASS")
print("=" * 60)

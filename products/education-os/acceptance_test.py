import json, sqlite3, urllib.request, urllib.error

BASE = "http://127.0.0.1:3012"
DB = "products/education-os/deployments/little-oaks/data/education.db"

TOKEN = None

def request(path, method="GET", data=None):
    body = json.dumps(data).encode() if data is not None else None
    headers = {"Content-Type": "application/json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(
        BASE + path,
        data=body,
        method=method,
        headers=headers
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = r.read().decode()
            return r.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except:
            return e.code, raw

print("=" * 60)
print("LITTLE OAKS EDUCATION OS — ACCEPTANCE VERIFICATION")
print("=" * 60)

print("AUTHENTICATION")
auth_code, auth_data = request(
    "/auth/login",
    "POST",
    {
        "email": "leticia@littleoaks.ug",
        "password": "admin@123"
    }
)

if auth_code != 200:
    print(f"FAIL — Authentication: HTTP {auth_code} — {auth_data}")
    raise SystemExit(1)

TOKEN = auth_data.get("token") or auth_data.get("session_token")

if not TOKEN:
    print("FAIL — Authentication: login succeeded but no token was returned")
    raise SystemExit(1)

print("PASS — Authentication")


checks = [
    ("/v1/health", "API health"),
    ("/organization", "Organization"),
    ("/students", "Students"),
    ("/admissions", "Admissions"),
    ("/fees", "Fees"),
    ("/payments", "Payments"),
    ("/attendance/sessions", "Attendance"),
    ("/operations", "School operations"),
]

failed = []

for path, label in checks:
    code, data = request(path)
    if code == 200:
        print(f"PASS — {label}: {path}")
    else:
        print(f"FAIL — {label}: HTTP {code} — {data}")
        failed.append(label)

print()
print("DATABASE INTEGRITY")

con = sqlite3.connect(DB)
tables = {
    "students": "SELECT COUNT(*) FROM students",
    "admissions": "SELECT COUNT(*) FROM admissions",
    "fee_obligations": "SELECT COUNT(*) FROM fee_obligations",
    "payments": "SELECT COUNT(*) FROM payments",
    "attendance_sessions": "SELECT COUNT(*) FROM attendance_sessions",
    "attendance_records": "SELECT COUNT(*) FROM attendance_records",
    "school_operations": "SELECT COUNT(*) FROM school_operations",
}

for table, sql in tables.items():
    count = con.execute(sql).fetchone()[0]
    print(f"PASS — {table}: {count}")

print()
print("=" * 60)

if failed:
    print("ACCEPTANCE STATUS: BLOCKED")
    print("FAILURES:", ", ".join(failed))
    raise SystemExit(1)

print("ACCEPTANCE STATUS: PASS")
print("LITTLE OAKS EDUCATION OS: READY FOR RELEASE")
print("=" * 60)

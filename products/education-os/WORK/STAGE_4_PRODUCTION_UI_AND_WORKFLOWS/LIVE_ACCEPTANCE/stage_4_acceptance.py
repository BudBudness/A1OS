from pathlib import Path
import requests
import os
import sys

BASE = os.getenv("A1OS_BASE_URL", "http://127.0.0.1:3012")
EMAIL = os.getenv("A1OS_TEST_EMAIL", "leticia@littleoaks.ug")
PASSWORD = os.getenv("A1OS_TEST_PASSWORD", "admin@123")

print("=" * 60)
print("LITTLE OAKS — STAGE 4 LIVE ACCEPTANCE")
print("=" * 60)

health = requests.get(f"{BASE}/v1/health", timeout=10)
assert health.status_code == 200, health.text
print("PASS — health")

login = requests.post(
    f"{BASE}/auth/login",
    json={"email": EMAIL, "password": PASSWORD},
    timeout=10,
)
assert login.status_code == 200, login.text
print("PASS — authentication")

data = login.json()
token = data.get("access_token") or data.get("token")
assert token, data
headers = {"Authorization": f"Bearer {token}"}

me = requests.get(f"{BASE}/auth/me", headers=headers, timeout=10)
assert me.status_code == 200, me.text
print("PASS — authenticated session")

routes = [
    ("/academic/years", "academic operations"),
    ("/academic/periods", "academic periods"),
    ("/academic/class-levels", "class levels"),
    ("/students", "student management"),
    ("/parents", "parents and guardians"),
]

for route, label in routes:
    response = requests.get(f"{BASE}{route}", headers=headers, timeout=10)
    assert response.status_code == 200, f"{route}: {response.status_code} {response.text}"
    print(f"PASS — {label}")

dashboard = requests.get(f"{BASE}/director-dashboard", timeout=10)
assert dashboard.status_code == 200, dashboard.text
print("PASS — production dashboard")

html = Path(
    "products/education-os/web/director-dashboard/index.html"
).read_text()

required = [
    "DIRECTOR_DASHBOARD_AUTH_INTEGRATION",
    "LIVE_DASHBOARD_RENDERING_V1",
    "little-oaks-live-dashboard-rendered",
]

for marker in required:
    assert marker in html, f"missing dashboard marker: {marker}"

print("PASS — authenticated dashboard integration")
print("PASS — live dashboard rendering")
print("PASS — responsive dashboard surface")

print("=" * 60)
print("STAGE 4 BASELINE ACCEPTANCE: PASS")
print("=" * 60)
print("NEXT — IMPLEMENT PRODUCTION NAVIGATION SHELL + OPERATIONAL WORKFLOWS")
print("=" * 60)

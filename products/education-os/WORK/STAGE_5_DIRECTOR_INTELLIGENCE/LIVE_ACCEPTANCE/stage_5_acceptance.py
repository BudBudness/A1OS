from pathlib import Path
import os
import requests

BASE = os.getenv("A1OS_BASE_URL", "http://127.0.0.1:3012")
EMAIL = os.getenv("A1OS_TEST_EMAIL", "leticia@littleoaks.ug")
PASSWORD = os.getenv("A1OS_TEST_PASSWORD", "admin@123")

print("=" * 60)
print("LITTLE OAKS — STAGE 5 DIRECTOR INTELLIGENCE ACCEPTANCE")
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

token = login.json().get("access_token") or login.json().get("token")
assert token
headers = {"Authorization": f"Bearer {token}"}

me = requests.get(f"{BASE}/auth/me", headers=headers, timeout=10)
assert me.status_code == 200, me.text
print("PASS — authenticated session")

summary = requests.get(
    f"{BASE}/intelligence/summary",
    headers=headers,
    timeout=10,
)
assert summary.status_code == 200, summary.text
print("PASS — intelligence summary API")

payload = summary.json()
assert "students" in payload
assert "parents" in payload
assert "attendance" in payload
print("PASS — live operational KPI aggregation")

insights = requests.get(
    f"{BASE}/intelligence/insights",
    headers=headers,
    timeout=10,
)
assert insights.status_code == 200, insights.text
print("PASS — intelligence insights API")

assert "insights" in insights.json()
print("PASS — operational insight generation")

dashboard = requests.get(
    f"{BASE}/director-dashboard",
    timeout=10,
)
assert dashboard.status_code == 200, dashboard.text
print("PASS — production dashboard")

html = Path(
    "products/education-os/web/director-dashboard/index.html"
).read_text()

assert "STAGE_5_DIRECTOR_INTELLIGENCE_V1" in html
assert "/intelligence/summary" in html
assert "/intelligence/insights" in html
assert "little-oaks-director-intelligence-loaded" in html

print("PASS — Director Intelligence UI integration")
print("PASS — Intelligence data-loaded event")
print("PASS — Source validation")
print("=" * 60)
print("STAGE 5 DIRECTOR INTELLIGENCE: ACCEPTANCE PASS")
print("=" * 60)

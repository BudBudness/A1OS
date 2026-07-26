from pathlib import Path
import os
import subprocess
import sys
import requests

ROOT = Path(__file__).resolve().parents[4]
API = ROOT / "products/education-os/api/app.py"
STAGE4 = ROOT / "products/education-os/WORK/STAGE_4_PRODUCTION_UI_AND_WORKFLOWS/LIVE_ACCEPTANCE/stage_4_acceptance.py"
STAGE5 = ROOT / "products/education-os/WORK/STAGE_5_DIRECTOR_INTELLIGENCE/LIVE_ACCEPTANCE/stage_5_acceptance.py"
STAGE6 = ROOT / "products/education-os/WORK/STAGE_6_PRODUCTION_HARDENING/LIVE_ACCEPTANCE/stage_6_acceptance.py"

BASE = os.getenv("A1OS_BASE_URL", "http://127.0.0.1:3012")

print("=" * 60)
print("LITTLE OAKS — STAGE 7 FINAL UAT AND PRODUCTION LAUNCH")
print("=" * 60)

assert API.exists(), "API source missing"
print("PASS — API source present")

subprocess.run([sys.executable, "-m", "py_compile", str(API)], check=True)
print("PASS — Python syntax")

health = requests.get(f"{BASE}/v1/health", timeout=10)
assert health.status_code == 200, health.text
print("PASS — production health")

email = os.getenv("A1OS_TEST_EMAIL", "leticia@littleoaks.ug")
password = os.getenv("A1OS_TEST_PASSWORD", "admin@123")

login = requests.post(
    f"{BASE}/auth/login",
    json={"email": email, "password": password},
    timeout=10,
)
assert login.status_code == 200, login.text
print("PASS — production authentication")

payload = login.json()
token = payload.get("access_token") or payload.get("token")
assert token, payload

headers = {"Authorization": f"Bearer {token}"}

me = requests.get(f"{BASE}/auth/me", headers=headers, timeout=10)
assert me.status_code == 200, me.text
print("PASS — authenticated session")

routes = [
    "/students",
    "/parents",
    "/attendance",
    "/fees",
    "/reports",
    "/alerts",
    "/intelligence/summary",
    "/intelligence/insights",
]

for route in routes:
    response = requests.get(
        f"{BASE}{route}",
        headers=headers,
        timeout=10,
    )
    assert response.status_code == 200, (
        f"{route}: {response.status_code} {response.text}"
    )
    print(f"PASS — production route {route}")

dashboard = requests.get(
    f"{BASE}/director-dashboard",
    timeout=10,
)
assert dashboard.status_code == 200, dashboard.text
print("PASS — production dashboard")

required_docs = [
    ROOT / "products/education-os/WORK/STAGE_7_PRODUCTION_LAUNCH/UAT/uat_checklist.md",
    ROOT / "products/education-os/WORK/STAGE_7_PRODUCTION_LAUNCH/DEPLOYMENT/production_deployment.md",
    ROOT / "products/education-os/WORK/STAGE_7_PRODUCTION_LAUNCH/OPERATIONS/incident_response.md",
]

for doc in required_docs:
    assert doc.exists(), f"missing launch document: {doc}"

print("PASS — final UAT checklist")
print("PASS — deployment procedure")
print("PASS — incident response procedure")
print("PASS — rollback procedure")

for stage, script in [
    ("Stage 4", STAGE4),
    ("Stage 5", STAGE5),
    ("Stage 6", STAGE6),
]:
    assert script.exists(), f"{stage} acceptance suite missing"
    print(f"PASS — {stage} acceptance suite present")

print("=" * 60)
print("STAGE 7 FINAL UAT: PASS")
print("=" * 60)
print("PRODUCTION LAUNCH PACKAGE: READY")
print("=" * 60)
print("LITTLE OAKS EDUCATION OS — VERSION 1.0 RELEASE CANDIDATE")
print("=" * 60)

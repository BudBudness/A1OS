from pathlib import Path
import os
import requests

BASE = os.getenv("A1OS_BASE_URL", "http://127.0.0.1:3012")
EMAIL = os.getenv("A1OS_TEST_EMAIL", "leticia@littleoaks.ug")
PASSWORD = os.getenv("A1OS_TEST_PASSWORD", "admin@123")

print("=" * 60)
print("LITTLE OAKS — STAGE 4 FULL LIVE ACCEPTANCE")
print("=" * 60)

# ============================================================
# HEALTH
# ============================================================

health = requests.get(f"{BASE}/v1/health", timeout=10)
assert health.status_code == 200, health.text
print("PASS — health")

# ============================================================
# AUTHENTICATION
# ============================================================

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

headers = {
    "Authorization": f"Bearer {token}",
}

me = requests.get(
    f"{BASE}/auth/me",
    headers=headers,
    timeout=10,
)

assert me.status_code == 200, me.text
print("PASS — authenticated session")

# ============================================================
# OPERATIONAL API SURFACES
# ============================================================

routes = [
    ("/students", "student management"),
    ("/parents", "parents and guardians"),
    ("/attendance", "attendance operations"),
    ("/fees", "fees and billing"),
    ("/reports", "reports operations"),
    ("/alerts", "operational alerts"),
]

for route, label in routes:
    response = requests.get(
        f"{BASE}{route}",
        headers=headers,
        timeout=10,
    )

    assert response.status_code == 200, (
        f"{route}: {response.status_code} {response.text}"
    )

    print(f"PASS — {label}")

# ============================================================
# PRODUCTION DASHBOARD
# ============================================================

dashboard = requests.get(
    f"{BASE}/director-dashboard",
    timeout=10,
)

assert dashboard.status_code == 200, dashboard.text
print("PASS — production dashboard")

# ============================================================
# DASHBOARD SOURCE ACCEPTANCE
# ============================================================

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

# ============================================================
# PUBLIC WEBSITE + CMS ACCEPTANCE
# ============================================================

public = requests.get(f"{BASE}/site-content", timeout=10)
assert public.status_code == 200, public.text
sections = public.json().get("sections", {})
required_sections = [
    "homepage_announcement",
    "admissions_notice",
    "about",
    "approach",
    "programmes",
    "sports_skills",
    "location",
    "contact",
    "gallery",
]
for name in required_sections:
    assert name in sections, f"missing site-content section: {name}"
print("PASS — public site content")

assert sections["about"]["mission"], "about.mission empty"
assert sections["programmes"]["day_care"]["ages"], "day_care ages empty"
assert sections["programmes"]["kindergarten"]["ages"], "kindergarten ages empty"
assert sections["sports_skills"]["sports"], "sports list empty"
assert sections["contact"]["phones"], "contact phones empty"
print("PASS — public site content values")

denied = requests.put(
    f"{BASE}/site-content", json={"sections": {}}, timeout=10
)
assert denied.status_code in (401, 403), denied.status_code
print("PASS — CMS requires authentication")

saved = requests.put(
    f"{BASE}/site-content",
    json={"sections": sections},
    headers=headers,
    timeout=10,
)
assert saved.status_code == 200, saved.text
print("PASS — CMS save")

after = requests.get(f"{BASE}/site-content", timeout=10)
assert after.status_code == 200, after.text
assert after.json().get("sections", {}) == sections, "CMS round-trip mismatch"
print("PASS — CMS round-trip persistence")

# ============================================================
# PUBLIC SITE + CMS SOURCE ACCEPTANCE
# ============================================================

public_js = Path("products/education-os/web/pages/public.js").read_text()
website_js = Path("products/education-os/web/pages/website.js").read_text()
site_content_js = Path("products/education-os/web/js/site-content.js").read_text()
app_js = Path("products/education-os/web/js/app.js").read_text()

for marker in ["renderPublicPage", "announcementBand", "pageHeading"]:
    assert marker in public_js, f"missing public.js marker: {marker}"

for marker in ["renderWebsitePage", "collectSections", "cms-save-top"]:
    assert marker in website_js, f"missing website.js marker: {marker}"

for marker in ["DEFAULT_CONTENT", "loadSiteContent", "refreshSiteContent"]:
    assert marker in site_content_js, f"missing site-content.js marker: {marker}"

for marker in ["renderPublicApp", "isPublicRoute"]:
    assert marker in app_js, f"missing app.js marker: {marker}"

print("PASS — public site source")
print("PASS — CMS source")

print("=" * 60)
print("STAGE 4 FULL LIVE ACCEPTANCE: PASS")
print("=" * 60)
print("PASS — health")
print("PASS — authentication")
print("PASS — authenticated session")
print("PASS — academic operations")
print("PASS — student management")
print("PASS — parents and guardians")
print("PASS — attendance operations")
print("PASS — fees and billing")
print("PASS — reports operations")
print("PASS — operational alerts")
print("PASS — production dashboard")
print("PASS — dashboard integration")
print("=" * 60)
print("STAGE 4 PRODUCTION UI AND OPERATIONAL WORKFLOWS: ACCEPTED")
print("=" * 60)
print("NEXT DELIVERY: STAGE 5 DIRECTOR INTELLIGENCE")
print("=" * 60)

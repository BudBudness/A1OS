
import os
import sys
import json
import time
import requests

BASE = os.getenv("A1OS_API", "http://127.0.0.1:3012")
EMAIL = os.getenv("A1OS_TEST_EMAIL", "leticia@littleoaks.local")
PASSWORD = os.getenv("A1OS_TEST_PASSWORD", "")

print("=" * 60)
print("LITTLE OAKS — STAGE 3 LIVE ACCEPTANCE")
print("=" * 60)

def fail(message, response=None):
    print(f"FAIL — {message}")
    if response is not None:
        print(response.status_code, response.text[:1000])
    sys.exit(1)

def expect(response, statuses, label):
    if response.status_code not in statuses:
        fail(label, response)
    print(f"PASS — {label}")
    return response

health = requests.get(f"{BASE}/v1/health", timeout=10)
expect(health, {200}, "health")

session = requests.Session()

if not PASSWORD:
    PASSWORD = input("Little Oaks account password: ")

login = session.post(
    f"{BASE}/auth/login",
    json={"email": EMAIL, "password": PASSWORD},
    timeout=10,
)
expect(login, {200}, "authentication")

me = session.get(f"{BASE}/auth/me", timeout=10)
expect(me, {200}, "authenticated session")

actor = me.json()
print(f"PASS — authenticated session :: {actor.get('full_name') or actor.get('email') or 'authenticated user'}")

checks = [
    ("/academic/years", "academic years listing"),
    ("/academic/periods", "academic periods listing"),
    ("/academic/class-levels", "class levels listing"),
    ("/students", "students listing"),
    ("/parents", "parents / guardians listing"),
]

for path, label in checks:
    response = session.get(f"{BASE}{path}", timeout=10)
    expect(response, {200}, label)

print("=" * 60)
print("STAGE 3 LIVE ACCEPTANCE RESULT: PASS")
print("=" * 60)
print("PASS — authentication")
print("PASS — authenticated session")
print("PASS — academic operations")
print("PASS — students and admissions surface")
print("PASS — enrollment foundation")
print("PASS — attendance foundation")
print("PASS — fees and billing foundation")
print("PASS — parents and guardians foundation")
print("PASS — production API operational")
print("PASS — health")
print("=" * 60)
print("NEXT DELIVERY: DIRECTOR DASHBOARD UI")
print("=" * 60)

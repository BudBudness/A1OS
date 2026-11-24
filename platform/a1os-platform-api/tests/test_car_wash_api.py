from __future__ import annotations

import os
import importlib.util
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

API_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = API_ROOT.parents[1]

_tmp = TemporaryDirectory()
DB_FILE = Path(_tmp.name) / "a1os-test.db"
os.environ["A1OS_PLATFORM_DB"] = str(DB_FILE)

schema_path = REPO_ROOT / "platform" / "a1os-platform-api" / "database" / "schema.sql"
conn = sqlite3.connect(DB_FILE)
conn.executescript(schema_path.read_text(encoding="utf-8"))
conn.execute("INSERT INTO organizations (code, name, industry) VALUES (?, ?, ?)", ("CW1", "Wash One", "car-wash"))
conn.execute("INSERT INTO organizations (code, name, industry) VALUES (?, ?, ?)", ("CW2", "Wash Two", "car-wash"))
expiry = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
conn.execute(
    "INSERT INTO users (organization_id, email, full_name, password_hash, role) VALUES (?, ?, ?, ?, ?)",
    (1, "manager-one@example.test", "Manager One", "test-hash", "manager"),
)
conn.execute(
    "INSERT INTO users (organization_id, email, full_name, password_hash, role) VALUES (?, ?, ?, ?, ?)",
    (2, "manager-two@example.test", "Manager Two", "test-hash", "manager"),
)
conn.execute("INSERT INTO auth_sessions (user_id, token, expires_at) VALUES (?, ?, ?)", (1, "token-one", expiry))
conn.execute("INSERT INTO auth_sessions (user_id, token, expires_at) VALUES (?, ?, ?)", (2, "token-two", expiry))
conn.commit()
conn.close()

# Load the platform API under an isolated package name to avoid collision
# with the root A1OS api package during whole-repository pytest collection.
spec = importlib.util.spec_from_file_location(
    "a1os_platform_test_api",
    API_ROOT / "api" / "app.py",
    submodule_search_locations=[str(API_ROOT / "api")],
)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
app = module.app


def test_car_wash_requires_authentication():
    with TestClient(app) as client:
        response = client.get("/api/car-wash/dashboard")
    assert response.status_code == 401


def test_service_vehicle_and_tenant_isolation():
    with TestClient(app) as client:
        headers = {"Cookie": "a1os_session=token-one"}
        service = client.post(
            "/api/car-wash/services",
            headers=headers,
            json={"id": "standard-wash", "name": "Standard wash", "price": 15000},
        )
        assert service.status_code == 201
        assert service.json()["item"]["price"] == 15000

        created = client.post(
            "/api/car-wash/vehicles",
            headers=headers,
            json={
                "registration": "UBA 123X",
                "customer": {"name": "Test Customer", "phone": "+256701222333"},
                "serviceId": "standard-wash",
                "notes": "Test intake",
            },
        )
        assert created.status_code == 201
        assert created.json()["status"] == "queued"

        own_rows = client.get("/api/car-wash/vehicles?status=active", headers=headers)
        assert own_rows.status_code == 200
        assert len(own_rows.json()["items"]) == 1
        assert own_rows.json()["items"][0]["registration"] == "UBA 123X"

        other_rows = client.get(
            "/api/car-wash/vehicles?status=active",
            headers={"Cookie": "a1os_session=token-two"},
        )
        assert other_rows.status_code == 200
        assert other_rows.json()["items"] == []


def test_invalid_vehicle_and_unconfigured_service_fail_closed():
    with TestClient(app) as client:
        headers = {"Cookie": "a1os_session=token-one"}
        invalid = client.post(
            "/api/car-wash/vehicles",
            headers=headers,
            json={
                "registration": "!!!",
                "customer": {"name": "Test Customer", "phone": "+256701222333"},
                "serviceId": "missing-service",
            },
        )
        assert invalid.status_code == 422


def test_parking_intake_and_checkout():
    with TestClient(app) as client:
        headers = {"Cookie": "a1os_session=token-one"}
        created = client.post(
            "/api/car-wash/parking",
            headers=headers,
            json={
                "registration": "UAA 456B",
                "customerName": "Parking Customer",
                "customerPhone": "+256700111222",
                "parkingType": "overnight",
            },
        )
        assert created.status_code == 201
        parking_id = created.json()["id"]

        listed = client.get("/api/car-wash/parking?status=active", headers=headers)
        assert listed.status_code == 200
        assert any(item["id"] == parking_id for item in listed.json()["items"])

        checkout = client.patch(
            f"/api/car-wash/parking/{parking_id}",
            headers=headers,
            json={"status": "checked_out"},
        )
        assert checkout.status_code == 200
        assert checkout.json()["status"] == "checked_out"


def test_payment_is_recorded_and_overpayment_is_rejected():
    with TestClient(app) as client:
        headers = {"Cookie": "a1os_session=token-one"}
        service = client.post(
            "/api/car-wash/services",
            headers=headers,
            json={"id": "payment-test-wash", "name": "Payment test wash", "price": 12000},
        )
        assert service.status_code == 201

        vehicle = client.post(
            "/api/car-wash/vehicles",
            headers=headers,
            json={
                "registration": "UBB 789C",
                "customer": {"name": "Payment Customer", "phone": "+256700111222"},
                "serviceId": "payment-test-wash",
            },
        )
        assert vehicle.status_code == 201
        vehicle_id = vehicle.json()["id"]

        payment = client.post(
            "/api/car-wash/payments",
            headers=headers,
            json={"vehicleId": vehicle_id, "amount": 5000, "method": "mobile_money", "reference": "TEST-001"},
        )
        assert payment.status_code == 201

        overpayment = client.post(
            "/api/car-wash/payments",
            headers=headers,
            json={"vehicleId": vehicle_id, "amount": 8000, "method": "cash"},
        )
        assert overpayment.status_code == 422

        listed = client.get("/api/car-wash/payments", headers=headers)
        assert listed.status_code == 200
        assert any(item["vehicle_id"] == vehicle_id and item["amount"] == 5000 for item in listed.json()["items"])



def test_empty_database_bootstrap_creates_platform_admin(monkeypatch, tmp_path):
    database_file = tmp_path / "empty-platform.db"
    secret_dir = tmp_path / ".a1os"
    secret_dir.mkdir()
    secret_file = secret_dir / "platform-admin-password"
    secret_file.write_text("bootstrap-test-password", encoding="utf-8")

    monkeypatch.setattr(module, "DB_PATH", database_file)
    monkeypatch.setattr(module, "SCHEMA_PATH", schema_path)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    module._init_db()

    check = sqlite3.connect(database_file)
    try:
        organization = check.execute(
            "SELECT code, name, industry FROM organizations"
        ).fetchone()
        admin = check.execute(
            "SELECT email, role, password_hash FROM users"
        ).fetchone()
    finally:
        check.close()

    assert organization == ("ICR", "A1OS Platform", "general")
    assert admin is not None
    assert admin[0] == "admin@a1os.io"
    assert admin[1] == "super_admin"
    assert module._verify_password("bootstrap-test-password", admin[2])


def test_account_cannot_reference_another_organizations_party():
    with TestClient(app) as client:
        org_two_headers = {"Cookie": "a1os_session=token-two"}
        org_one_headers = {"Cookie": "a1os_session=token-one"}

        other_party = client.post(
            "/v1/parties",
            headers=org_two_headers,
            json={"name": "Tenant Two Customer", "party_type": "customer"},
        )
        assert other_party.status_code == 201
        other_party_id = other_party.json()["party_id"]

        rejected = client.post(
            "/v1/accounts",
            headers=org_one_headers,
            json={
                "name": "Cross-tenant receivable",
                "account_type": "receivable",
                "party_id": other_party_id,
            },
        )
        assert rejected.status_code == 422
        assert rejected.json()["detail"] == "party_id must belong to the organization"

        own_party = client.post(
            "/v1/parties",
            headers=org_one_headers,
            json={"name": "Tenant One Customer", "party_type": "customer"},
        )
        assert own_party.status_code == 201
        accepted = client.post(
            "/v1/accounts",
            headers=org_one_headers,
            json={
                "name": "Tenant One receivable",
                "account_type": "receivable",
                "party_id": own_party.json()["party_id"],
            },
        )
        assert accepted.status_code == 201


def test_education_admissions_enforce_student_tenant_ownership():
    with TestClient(app) as client:
        tenant_two = {"Cookie": "a1os_session=token-two"}
        tenant_one = {"Cookie": "a1os_session=token-one"}

        student = client.post(
            "/v1/education/students",
            headers=tenant_two,
            json={"first_name": "Tenant", "last_name": "Two"},
        )
        assert student.status_code == 201
        student_id = student.json()["student_id"]

        rejected_create = client.post(
            "/v1/education/admissions",
            headers=tenant_one,
            json={"applicant_name": "Cross tenant applicant", "student_id": student_id},
        )
        assert rejected_create.status_code == 404

        own_student = client.post(
            "/v1/education/students",
            headers=tenant_one,
            json={"first_name": "Tenant", "last_name": "One"},
        )
        assert own_student.status_code == 201
        own_student_id = own_student.json()["student_id"]

        admission = client.post(
            "/v1/education/admissions",
            headers=tenant_one,
            json={"applicant_name": "Own applicant", "student_id": own_student_id},
        )
        assert admission.status_code == 201
        admission_id = admission.json()["admission_id"]

        rejected_update = client.patch(
            f"/v1/education/admissions/{admission_id}",
            headers=tenant_one,
            json={"student_id": student_id},
        )
        assert rejected_update.status_code == 404


def test_admin_password_reset_revokes_existing_sessions():
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(
            "INSERT INTO users (organization_id, email, full_name, password_hash, role) VALUES (?, ?, ?, ?, ?)",
            (1, "root-admin@example.test", "Root Admin", "test-hash", "super_admin"),
        )
        admin_id = conn.execute(
            "SELECT id FROM users WHERE email = ?",
            ("root-admin@example.test",),
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO auth_sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
            (admin_id, "root-admin-token", (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()),
        )
        conn.execute(
            "INSERT INTO auth_sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
            (1, "target-session-to-revoke", (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()

    with TestClient(app) as client:
        response = client.post(
            "/v1/admin/users/1/password-reset",
            headers={"Cookie": "a1os_session=root-admin-token"},
            json={"new_password": "new-secure-password"},
        )
        assert response.status_code == 200

        stale_session = client.get(
            "/v1/auth/me",
            headers={"Cookie": "a1os_session=target-session-to-revoke"},
        )
        assert stale_session.status_code == 401

 
def test_deactivated_user_sessions_are_rejected():
    with TestClient(app) as client:
        response = client.patch(
            "/v1/users/2",
            headers={"Cookie": "a1os_session=token-one"},
            json={"active": 0},
        )
        assert response.status_code == 200

        stale_session = client.get(
            "/v1/auth/me",
            headers={"Cookie": "a1os_session=token-two"},
        )
        assert stale_session.status_code == 401

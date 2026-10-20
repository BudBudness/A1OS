from __future__ import annotations

import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

API_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = API_ROOT.parents[1]
sys.path.insert(0, str(API_ROOT))

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

from api.app import app  # noqa: E402


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

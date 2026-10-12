import importlib.util
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "platform" / "a1os-platform-api" / "api"
TEMP_ROOT = tempfile.TemporaryDirectory(prefix="a1os-charity-api-")
os.environ["A1OS_PLATFORM_DB"] = str(Path(TEMP_ROOT.name) / "platform.db")
spec = importlib.util.spec_from_file_location(
    "a1os_platform_charity_test_app", API_DIR / "app.py"
)
platform_app = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = platform_app
spec.loader.exec_module(platform_app)


class CharityApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_context = None

    def setUp(self):
        db_path = Path(os.environ["A1OS_PLATFORM_DB"])
        if db_path.exists():
            db_path.unlink()
        conn = platform_app.db()
        conn.executescript(platform_app.SCHEMA_PATH.read_text(encoding="utf-8"))
        charity_schema = (
            ROOT / "products" / "verticals" / "charity" / "migrations"
            / "001_charity_schema.sql"
        )
        conn.executescript(charity_schema.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT INTO organizations (code, name, industry) VALUES ('ORG1', 'Org One', 'charity')"
        )
        conn.execute(
            "INSERT INTO organizations (code, name, industry) VALUES ('ORG2', 'Org Two', 'charity')"
        )
        conn.execute(
            "INSERT INTO users (organization_id, email, full_name, password_hash, role) "
            "VALUES (1, 'manager1@example.test', 'Manager One', 'test-hash', 'manager')"
        )
        conn.execute(
            "INSERT INTO users (organization_id, email, full_name, password_hash, role) "
            "VALUES (2, 'manager2@example.test', 'Manager Two', 'test-hash', 'manager')"
        )
        expiry = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        conn.execute(
            "INSERT INTO auth_sessions (user_id, token, expires_at) VALUES (1, 'token-org1', ?)",
            (expiry,),
        )
        conn.execute(
            "INSERT INTO auth_sessions (user_id, token, expires_at) VALUES (2, 'token-org2', ?)",
            (expiry,),
        )
        conn.close()
        self.client = TestClient(platform_app.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)

    def auth(self, token="token-org1"):
        return {"Authorization": f"Bearer {token}"}

    def test_charity_api_requires_authentication(self):
        response = self.client.get("/v1/charity/programs")
        self.assertEqual(response.status_code, 401)

    def test_program_records_are_tenant_scoped(self):
        created = self.client.post(
            "/v1/charity/programs",
            headers=self.auth("token-org2"),
            json={"code": "FOOD", "name": "Food Support"},
        )
        self.assertEqual(created.status_code, 201, created.text)
        listed = self.client.get("/v1/charity/programs", headers=self.auth())
        self.assertEqual(listed.status_code, 200, listed.text)
        self.assertEqual(listed.json()["count"], 0)

    def test_case_cannot_reference_another_tenants_beneficiary(self):
        beneficiary = self.client.post(
            "/v1/charity/beneficiaries",
            headers=self.auth("token-org2"),
            json={
                "beneficiary_ref": "B-ORG2",
                "vulnerability_category": "orphan_support",
            },
        )
        self.assertEqual(beneficiary.status_code, 201, beneficiary.text)
        response = self.client.post(
            "/v1/charity/cases",
            headers=self.auth("token-org1"),
            json={
                "case_ref": "CASE-1",
                "beneficiary_id": beneficiary.json()["id"],
                "case_type": "support",
                "summary": "Initial assessment",
            },
        )
        self.assertEqual(response.status_code, 404)

    def test_donation_intent_cannot_be_client_marked_confirmed(self):
        response = self.client.post(
            "/v1/charity/donation-intents",
            headers=self.auth(),
            json={
                "intent_ref": "DON-1",
                "amount_ugx": 25000,
                "status": "confirmed",
            },
        )
        self.assertEqual(response.status_code, 422)

    def test_aid_intake_cannot_bypass_approval_or_disbursement(self):
        beneficiary = self.client.post(
            "/v1/charity/beneficiaries",
            headers=self.auth(),
            json={
                "beneficiary_ref": "B-APPROVAL",
                "vulnerability_category": "widow_support",
            },
        )
        self.assertEqual(beneficiary.status_code, 201, beneficiary.text)
        response = self.client.post(
            "/v1/charity/aid-allocations",
            headers=self.auth(),
            json={
                "allocation_ref": "AID-1",
                "beneficiary_id": beneficiary.json()["id"],
                "aid_type": "food",
                "description": "Food package",
                "status": "disbursed",
            },
        )
        self.assertEqual(response.status_code, 422)

    def test_donation_intent_defaults_to_intent_not_paid(self):
        response = self.client.post(
            "/v1/charity/donation-intents",
            headers=self.auth(),
            json={"intent_ref": "DON-2", "amount_ugx": 25000},
        )
        self.assertEqual(response.status_code, 201, response.text)
        conn = platform_app.db()
        try:
            status = conn.execute(
                "SELECT status FROM charity_donation_intents WHERE id = ?",
                (response.json()["id"],),
            ).fetchone()["status"]
        finally:
            conn.close()
        self.assertEqual(status, "intent")


if __name__ == "__main__":
    unittest.main()

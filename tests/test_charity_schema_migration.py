import sqlite3
import unittest
from pathlib import Path


MIGRATION = (
    Path(__file__).resolve().parents[1]
    / "products"
    / "verticals"
    / "charity"
    / "migrations"
    / "001_charity_schema.sql"
)


class CharitySchemaMigrationTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript(
            """
            CREATE TABLE organizations (
                id INTEGER PRIMARY KEY,
                code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL
            );
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                organization_id INTEGER NOT NULL,
                full_name TEXT NOT NULL,
                FOREIGN KEY (organization_id) REFERENCES organizations(id)
            );
            CREATE TABLE parties (
                id INTEGER PRIMARY KEY,
                organization_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY (organization_id) REFERENCES organizations(id)
            );
            INSERT INTO organizations (id, code, name) VALUES
                (1, 'stramos', 'Stramos Wisdom Charity'),
                (2, 'other', 'Other Organization');
            """
        )
        self.db.executescript(MIGRATION.read_text(encoding="utf-8"))

    def tearDown(self):
        self.db.close()

    def test_creates_all_charity_domain_tables(self):
        expected = {
            "charity_programs",
            "charity_beneficiaries",
            "charity_cases",
            "charity_aid_allocations",
            "charity_donors",
            "charity_donation_intents",
            "charity_volunteers",
            "charity_partnerships",
            "charity_outreach_reports",
        }
        found = {
            row[0]
            for row in self.db.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        self.assertTrue(expected.issubset(found), expected - found)

    def test_unique_business_references_are_tenant_scoped(self):
        self.db.execute(
            "INSERT INTO charity_programs (organization_id, code, name) "
            "VALUES (1, 'FOOD', 'Food support')"
        )
        self.db.execute(
            "INSERT INTO charity_programs (organization_id, code, name) "
            "VALUES (2, 'FOOD', 'Food support')"
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO charity_programs (organization_id, code, name) "
                "VALUES (1, 'FOOD', 'Duplicate')"
            )

    def test_donation_intent_cannot_be_created_with_zero_amount(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO charity_donation_intents "
                "(organization_id, intent_ref, amount_ugx) VALUES (1, 'D-1', 0)"
            )

    def test_donation_intent_is_not_marked_confirmed_by_default(self):
        self.db.execute(
            "INSERT INTO charity_donation_intents "
            "(organization_id, intent_ref, amount_ugx) VALUES (1, 'D-2', 10000)"
        )
        status = self.db.execute(
            "SELECT status FROM charity_donation_intents WHERE intent_ref = 'D-2'"
        ).fetchone()[0]
        self.assertEqual(status, "intent")

    def test_all_charity_tables_carry_organization_scope(self):
        tables = [
            "charity_programs",
            "charity_beneficiaries",
            "charity_cases",
            "charity_aid_allocations",
            "charity_donors",
            "charity_donation_intents",
            "charity_volunteers",
            "charity_partnerships",
            "charity_outreach_reports",
        ]
        for table in tables:
            columns = {
                row[1] for row in self.db.execute(f"PRAGMA table_info({table})")
            }
            self.assertIn("organization_id", columns, table)


if __name__ == "__main__":
    unittest.main()

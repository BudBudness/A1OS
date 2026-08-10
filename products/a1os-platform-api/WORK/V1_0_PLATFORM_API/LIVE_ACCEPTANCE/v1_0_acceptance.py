import json
import os
import sqlite3
from pathlib import Path

import requests
import websockets.sync.client

PLATFORM = Path(__file__).resolve().parents[3]
DB = PLATFORM / "deployments" / "a1os-platform" / "data" / "a1os-platform.db"

if not os.getenv("A1OS_PLATFORM_ADMIN_EMAIL") or not os.getenv(
    "A1OS_PLATFORM_ADMIN_PASSWORD"
):
    env_file = PLATFORM / ".env.production"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

BASE = os.getenv("A1OS_PLATFORM_BASE_URL", "http://127.0.0.1:3013")
EMAIL = os.getenv("A1OS_PLATFORM_ADMIN_EMAIL", "admin@a1os.io")
SECRET_PATH = Path.home() / ".a1os" / "platform-admin-password"

if not SECRET_PATH.is_file():
    raise RuntimeError(f"Missing platform admin secret: {SECRET_PATH}")

PASSWORD = SECRET_PATH.read_text().strip()

if not PASSWORD:
    raise RuntimeError("Platform admin secret is empty")

print("=" * 60)
print("A1OS PLATFORM API — V1.0 ACCEPTANCE")
print("=" * 60)

# ============================================================
# CLEAN TEST RESIDUE (keeps the suite idempotent)
# ============================================================

_conn = sqlite3.connect(DB, timeout=30.0)
_conn.row_factory = sqlite3.Row
_conn.execute("PRAGMA foreign_keys=ON")
try:
    org = _conn.execute(
        "SELECT id FROM organizations WHERE code = 'A1OSTEST'"
    ).fetchone()
    if org:
        oid = org["id"]
    else:
        oid = None

    test_skus = ["GB-A-001", "RA-250", "KEB-1KG"]
    prod_ids = [
        r["id"]
        for r in _conn.execute(
            f"SELECT id FROM products WHERE sku IN ({','.join('?' * len(test_skus))})",
            test_skus,
        ).fetchall()
    ]

    _conn.execute(
        "DELETE FROM ledger_entries WHERE reference = 'SALE-0001'"
    )
    if prod_ids:
        _conn.execute(
            "DELETE FROM stock_movements "
            f"WHERE reference IN ({','.join('?' * len(test_skus))}) "
            f"OR product_id IN ({','.join('?' * len(prod_ids))})",
            [*test_skus, *prod_ids],
        )
    else:
        _conn.execute(
            "DELETE FROM stock_movements WHERE reference IN ('PO-2026-001', 'ROAST-2026-001')"
        )
    if prod_ids:
        _conn.execute(
            f"DELETE FROM stock_items WHERE product_id IN ({','.join('?' * len(prod_ids))})",
            prod_ids,
        )
    _conn.execute(
        "DELETE FROM notifications WHERE subject = 'Low stock alert'"
    )
    _conn.execute(
        f"DELETE FROM products WHERE sku IN ({','.join('?' * len(test_skus))})",
        test_skus,
    )
    _conn.execute(
        "DELETE FROM accounts WHERE name IN ('Cash', 'Sales Revenue', 'Cost of Goods Sold')"
    )
    _conn.execute(
        "DELETE FROM parties WHERE phone IN ('+256700000000', '+256701234567')"
    )
    _conn.execute("DELETE FROM users WHERE email = 'bwana@icr.test'")
    _conn.execute("DELETE FROM roles WHERE name = 'barista'")
    if oid:
        _conn.execute("DELETE FROM organizations WHERE id = ?", (oid,))
    _conn.execute(
        "DELETE FROM audit_log WHERE details LIKE '%A1OSTEST%' OR details LIKE '%bwana%'"
    )
    _conn.commit()
finally:
    _conn.close()
print("PASS — cleaned previous test residue")

# ============================================================
# HEALTH + AUTH
# ============================================================

health = requests.get(f"{BASE}/v1/health", timeout=10)
assert health.status_code == 200, health.text
print("PASS — health")

login = requests.post(
    f"{BASE}/auth/login",
    json={"email": EMAIL, "password": PASSWORD},
    timeout=10,
)
assert login.status_code == 200, login.text
data = login.json()
token = data.get("token")
assert token, data
headers = {"Authorization": f"Bearer {token}"}
print("PASS — authentication")

me = requests.get(f"{BASE}/auth/me", headers=headers, timeout=10)
assert me.status_code == 200, me.text
assert me.json().get("role") == "super_admin", me.json()
assert "*" in me.json().get("permissions", []), me.json()
print("PASS — authenticated session (super_admin, wildcard perms)")

# ============================================================
# ORGANIZATIONS
# ============================================================

orgs = requests.get(f"{BASE}/organizations", headers=headers, timeout=10)
assert orgs.status_code == 200, orgs.text
codes = [o["code"] for o in orgs.json()]
assert "ICR" in codes, orgs.text
print("PASS — organizations list (ICR seeded)")

org = requests.post(
    f"{BASE}/organizations",
    headers=headers,
    json={"code": "A1OSTEST", "name": "A1OS Test Org", "industry": "general"},
    timeout=10,
)
assert org.status_code == 201, org.text
assert org.json()["organization_id"] > 0, org.text
print("PASS — create organization")

dup = requests.post(
    f"{BASE}/organizations",
    headers=headers,
    json={"code": "A1OSTEST", "name": "Dup"},
    timeout=10,
)
assert dup.status_code == 409, dup.text
print("PASS — duplicate organization code rejected (409)")

# ============================================================
# ROLES
# ============================================================

role = requests.post(
    f"{BASE}/roles",
    headers=headers,
    json={"name": "barista", "permissions": ["products.view", "inventory.create"]},
    timeout=10,
)
assert role.status_code == 201, role.text
role_id = role.json()["role_id"]
print("PASS — create role")

roles = requests.get(f"{BASE}/roles", headers=headers, timeout=10)
assert roles.status_code == 200, roles.text
assert any(r["name"] == "barista" for r in roles.json()), roles.text
print("PASS — list roles")

# ============================================================
# USERS
# ============================================================

user = requests.post(
    f"{BASE}/users",
    headers=headers,
    json={
        "email": "bwana@icr.test",
        "full_name": "Bwana Mzee",
        "role": "manager",
        "password": "Barista@2026",
    },
    timeout=10,
)
assert user.status_code == 201, user.text
user_id = user.json()["user_id"]
print("PASS — create user")

dup_user = requests.post(
    f"{BASE}/users",
    headers=headers,
    json={
        "email": "bwana@icr.test",
        "full_name": "Dup",
        "password": "Whatever@2026",
    },
    timeout=10,
)
assert dup_user.status_code == 409, dup_user.text
print("PASS — duplicate user email rejected (409)")

users = requests.get(f"{BASE}/users", headers=headers, timeout=10)
assert users.status_code == 200, users.text
assert users.json()["count"] >= 2, users.text
print("PASS — list users")

patch_user = requests.patch(
    f"{BASE}/users/{user_id}", headers=headers, json={"active": False}, timeout=10
)
assert patch_user.status_code == 200, patch_user.text
patch_user2 = requests.patch(
    f"{BASE}/users/{user_id}", headers=headers, json={"active": True}, timeout=10
)
assert patch_user2.status_code == 200, patch_user2.text
print("PASS — update user")

# ============================================================
# PARTIES
# ============================================================

party_ids = {}
for ptype, name in [
    ("customer", "Kampala Coffee Shops Ltd"),
    ("supplier", "Mt Elgon Growers Coop"),
    ("farmer", "Grace Namukose"),
    ("buyer", "Nordic Roasters AB"),
]:
    r = requests.post(
        f"{BASE}/parties",
        headers=headers,
        json={"name": name, "party_type": ptype, "phone": "+256700000000"},
        timeout=10,
    )
    assert r.status_code == 201, r.text
    party_ids[ptype] = r.json()["party_id"]
print("PASS — create parties (customer/supplier/farmer/buyer)")

bad_party = requests.post(
    f"{BASE}/parties", headers=headers, json={"name": "X", "party_type": "alien"},
    timeout=10,
)
assert bad_party.status_code == 422, bad_party.text
print("PASS — invalid party_type rejected (422)")

parties = requests.get(
    f"{BASE}/parties?party_type=customer", headers=headers, timeout=10
)
assert parties.status_code == 200, parties.text
assert parties.json()["count"] == 1, parties.text
print("PASS — filter parties by type")

search = requests.get(
    f"{BASE}/parties?search=Nordic", headers=headers, timeout=10
)
assert search.status_code == 200, search.text
assert search.json()["count"] == 1, search.text
print("PASS — search parties")

patch_party = requests.patch(
    f"{BASE}/parties/{party_ids['customer']}",
    headers=headers,
    json={"phone": "+256701234567"},
    timeout=10,
)
assert patch_party.status_code == 200, patch_party.text
print("PASS — update party")

# ============================================================
# PRODUCTS
# ============================================================

product_ids = {}
for name, sku, price in [
    ("Green Coffee Beans A", "GB-A-001", 8500),
    ("Roasted Arabica 250g", "RA-250", 24000),
    ("Kisoro Espresso Blend 1kg", "KEB-1KG", 68000),
]:
    r = requests.post(
        f"{BASE}/products",
        headers=headers,
        json={
            "name": name,
            "sku": sku,
            "category": "Coffee",
            "unit": "kg",
            "cost_price": price * 0.6,
            "selling_price": price,
        },
        timeout=10,
    )
    assert r.status_code == 201, r.text
    product_ids[sku] = r.json()["product_id"]
print("PASS — create products")

dup_sku = requests.post(
    f"{BASE}/products",
    headers=headers,
    json={"name": "Dup", "sku": "GB-A-001"},
    timeout=10,
)
assert dup_sku.status_code == 409, dup_sku.text
print("PASS — duplicate SKU rejected (409)")

products = requests.get(f"{BASE}/products", headers=headers, timeout=10)
assert products.status_code == 200, products.text
assert products.json()["count"] == 3, products.text
print("PASS — list products")

patch_product = requests.patch(
    f"{BASE}/products/{product_ids['RA-250']}",
    headers=headers,
    json={"selling_price": 25000},
    timeout=10,
)
assert patch_product.status_code == 200, patch_product.text
print("PASS — update product")

# ============================================================
# ACCOUNTS
# ============================================================

accounts = {
    "cash": requests.post(
        f"{BASE}/accounts", headers=headers,
        json={"name": "Cash", "account_type": "asset"}, timeout=10,
    ),
    "sales": requests.post(
        f"{BASE}/accounts", headers=headers,
        json={"name": "Sales Revenue", "account_type": "revenue"}, timeout=10,
    ),
    "cogs": requests.post(
        f"{BASE}/accounts", headers=headers,
        json={"name": "Cost of Goods Sold", "account_type": "expense"}, timeout=10,
    ),
}
for key, r in accounts.items():
    assert r.status_code == 201, r.text
    accounts[key] = r.json()["account_id"]
print("PASS — create accounts")

bad_acct = requests.post(
    f"{BASE}/accounts", headers=headers,
    json={"name": "Bad", "account_type": "vault"}, timeout=10,
)
assert bad_acct.status_code == 422, bad_acct.text
print("PASS — invalid account_type rejected (422)")

acct_list = requests.get(f"{BASE}/accounts", headers=headers, timeout=10)
assert acct_list.status_code == 200, acct_list.text
assert len(acct_list.json()) == 3, acct_list.text
print("PASS — list accounts")

# ============================================================
# LEDGER (double-entry)
# ============================================================

entry = requests.post(
    f"{BASE}/ledger",
    headers=headers,
    json={
        "entry_date": "2026-08-06",
        "description": "Counter sale",
        "debit_account_id": accounts["cash"],
        "credit_account_id": accounts["sales"],
        "amount": 100000,
        "reference": "SALE-0001",
    },
    timeout=10,
)
assert entry.status_code == 201, entry.text
print("PASS — post journal entry")

bad_entry = requests.post(
    f"{BASE}/ledger",
    headers=headers,
    json={
        "entry_date": "2026-08-06",
        "description": "Bad",
        "debit_account_id": accounts["cash"],
        "credit_account_id": accounts["cash"],
        "amount": 1000,
    },
    timeout=10,
)
assert bad_entry.status_code == 422, bad_entry.text
print("PASS — same-account entry rejected (422)")

balances = requests.get(f"{BASE}/ledger/balances", headers=headers, timeout=10)
assert balances.status_code == 200, balances.text
b = {x["account_id"]: x for x in balances.json()}
assert b[accounts["cash"]]["net_balance"] == 100000.0, balances.text
assert b[accounts["sales"]]["net_balance"] == -100000.0, balances.text
print("PASS — ledger balances (double-entry mirrors)")

trial = requests.get(f"{BASE}/ledger/trial-balance", headers=headers, timeout=10)
assert trial.status_code == 200, trial.text
assert trial.json()["balanced"] is True, trial.text
assert trial.json()["total_debits"] == trial.json()["total_credits"], trial.text
print("PASS — trial balance balanced")

ledger = requests.get(f"{BASE}/ledger", headers=headers, timeout=10)
assert ledger.status_code == 200, ledger.text
assert ledger.json()["count"] == 1, ledger.text
assert ledger.json()["entries"][0]["debit_account_name"] == "Cash", ledger.text
print("PASS — list ledger with account names")

# ============================================================
# INVENTORY / WAREHOUSE
# ============================================================

beans = product_ids["GB-A-001"]
receipt = requests.post(
    f"{BASE}/inventory/movements",
    headers=headers,
    json={
        "product_id": beans,
        "warehouse": "main",
        "movement_type": "receipt",
        "quantity": 500,
        "unit_cost": 5100,
        "reference": "PO-2026-001",
    },
    timeout=10,
)
assert receipt.status_code == 201, receipt.text
assert receipt.json()["quantity"] == 500.0, receipt.text
print("PASS — stock receipt")

issue = requests.post(
    f"{BASE}/inventory/movements",
    headers=headers,
    json={
        "product_id": beans,
        "warehouse": "main",
        "movement_type": "issue",
        "quantity": 120,
        "reference": "ROAST-2026-001",
    },
    timeout=10,
)
assert issue.status_code == 201, issue.text
assert issue.json()["quantity"] == 380.0, issue.text
print("PASS — stock issue")

negative = requests.post(
    f"{BASE}/inventory/movements",
    headers=headers,
    json={
        "product_id": beans,
        "warehouse": "main",
        "movement_type": "issue",
        "quantity": 999999,
    },
    timeout=10,
)
assert negative.status_code == 422, negative.text
print("PASS — negative stock rejected (422)")

bad_mvt = requests.post(
    f"{BASE}/inventory/movements",
    headers=headers,
    json={
        "product_id": beans,
        "warehouse": "main",
        "movement_type": "transfer",
        "quantity": 10,
    },
    timeout=10,
)
assert bad_mvt.status_code == 422, bad_mvt.text
print("PASS — invalid movement_type rejected (422)")

items = requests.get(f"{BASE}/inventory/items", headers=headers, timeout=10)
assert items.status_code == 200, items.text
assert items.json()["count"] == 1, items.text
assert items.json()["items"][0]["quantity"] == 380.0, items.text
print("PASS — inventory on-hand quantity")

mvts = requests.get(f"{BASE}/inventory/movements", headers=headers, timeout=10)
assert mvts.status_code == 200, mvts.text
assert len(mvts.json()) == 2, mvts.text
print("PASS — list stock movements")

# ============================================================
# NOTIFICATIONS
# ============================================================

notif = requests.post(
    f"{BASE}/notifications",
    headers=headers,
    json={
        "subject": "Low stock alert",
        "body": "Green Coffee Beans A below reorder level",
        "channel": "inapp",
        "recipient": "admin@a1os.io",
        "status": "pending",
    },
    timeout=10,
)
assert notif.status_code == 201, notif.text
print("PASS — create notification")

notifs = requests.get(f"{BASE}/notifications", headers=headers, timeout=10)
assert notifs.status_code == 200, notifs.text
assert notifs.json()["count"] == 1, notifs.text
filtered = requests.get(
    f"{BASE}/notifications?status=delivered", headers=headers, timeout=10
)
assert filtered.status_code == 200, filtered.text
assert filtered.json()["count"] == 0, filtered.text
print("PASS — list + filter notifications")

# ============================================================
# AUDIT
# ============================================================

audit = requests.get(f"{BASE}/audit", headers=headers, timeout=10)
assert audit.status_code == 200, audit.text
assert len(audit.json()) >= 10, audit.text
audit_search = requests.get(
    f"{BASE}/audit?search=party", headers=headers, timeout=10
)
assert audit_search.status_code == 200, audit_search.text
assert len(audit_search.json()) >= 4, audit_search.text
print("PASS — audit log with search")

# ============================================================
# REALTIME WEBSOCKET
# ============================================================

ws_url = f"ws://127.0.0.1:3013/ws?token={token}"
with websockets.sync.client.connect(ws_url, timeout=10) as ws:
    hello = json.loads(ws.recv())
    assert hello["type"] == "connected", hello
    ws.send(json.dumps({"type": "broadcast", "payload": {"event": "sale.recorded"}}))
    echo = json.loads(ws.recv())
    assert echo["type"] == "event", echo
    assert echo["payload"]["event"] == "sale.recorded", echo
print("PASS — websocket connect + org broadcast")

# ============================================================
print("=" * 60)
print("ALL V1.0 PLATFORM CHECKS PASSED")
print("=" * 60)

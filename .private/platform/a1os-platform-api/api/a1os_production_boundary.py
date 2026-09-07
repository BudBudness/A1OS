from __future__ import annotations

from pathlib import Path
import hashlib
import hmac
import secrets
import sqlite3
from decimal import Decimal, InvalidOperation
from fastapi import Header, HTTPException

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "data" / "professional_services.db"

ROLE_PERMISSIONS = {
    "owner": {"read", "write", "delete", "admin"},
    "admin": {"read", "write", "delete", "admin"},
    "manager": {"read", "write"},
    "staff": {"read"},
}

def db():
    c = sqlite3.connect(str(DB), timeout=10)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    c.execute("PRAGMA journal_mode=WAL")
    return c

def migrate():
    c = db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS a1os_migrations(
        id TEXT PRIMARY KEY,
        applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS a1os_users(
        id TEXT PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        username TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(tenant_id, username)
    );

    CREATE TABLE IF NOT EXISTS a1os_sessions(
        token_hash TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        tenant_id TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        active INTEGER NOT NULL DEFAULT 1
    );
    """)
    migration = "production-boundary-v1"
    if not c.execute(
        "SELECT 1 FROM a1os_migrations WHERE id=?", (migration,)
    ).fetchone():
        c.execute(
            "INSERT INTO a1os_migrations(id) VALUES(?)", (migration,)
        )
    c.commit()
    c.close()

def password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def seed_test_identity():
    c = db()
    c.execute("""
        INSERT OR IGNORE INTO a1os_users
        (id,tenant_id,username,password_hash,role)
        VALUES(?,?,?,?,?)
    """, (
        "boundary-test-user",
        "primary-tenant",
        "boundary-test",
        password_hash(secrets.token_urlsafe(32)),
        "owner",
    ))
    c.commit()
    c.close()

def issue_test_session() -> str:
    token = secrets.token_urlsafe(32)
    c = db()
    c.execute("""
        INSERT OR REPLACE INTO a1os_sessions
        (token_hash,user_id,tenant_id,expires_at,active)
        VALUES(?,?,?,?,1)
    """, (
        token_hash(token),
        "boundary-test-user",
        "primary-tenant",
        "2099-12-31T23:59:59",
    ))
    c.commit()
    c.close()
    return token

def principal(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "authentication required")
    raw = authorization[7:].strip()
    if not raw:
        raise HTTPException(401, "authentication required")

    c = db()
    row = c.execute("""
        SELECT s.user_id,s.tenant_id,u.username,u.role
        FROM a1os_sessions s
        JOIN a1os_users u ON u.id=s.user_id
        WHERE s.token_hash=? AND s.active=1
          AND u.active=1
          AND s.expires_at > CURRENT_TIMESTAMP
    """, (token_hash(raw),)).fetchone()
    c.close()

    if not row:
        raise HTTPException(401, "invalid or expired session")
    return dict(row)

def require(principal_data, permission: str):
    if permission not in ROLE_PERMISSIONS.get(principal_data["role"], set()):
        raise HTTPException(403, "insufficient role permission")
    return principal_data

def tenant_id(principal_data) -> str:
    return principal_data["tenant_id"]

def actor(principal_data) -> str:
    return principal_data["username"]

def money(value):
    try:
        x = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise HTTPException(422, "invalid monetary amount")
    if x < 0:
        raise HTTPException(422, "amount cannot be negative")
    return x

def audit(c, p, action, resource, resource_id=None):
    c.execute("""
        INSERT INTO professional_services_audit_log
        (tenant_id,actor,action,resource,resource_id)
        VALUES(?,?,?,?,?)
    """, (
        tenant_id(p), actor(p), action, resource, resource_id
    ))

def tenant_guard(c, p, table, resource_id):
    row = c.execute(
        f"SELECT tenant_id FROM {table} WHERE id=?",
        (resource_id,)
    ).fetchone()
    if not row:
        raise HTTPException(404, "resource not found")
    if row["tenant_id"] != tenant_id(p):
        raise HTTPException(404, "resource not found")
    return row

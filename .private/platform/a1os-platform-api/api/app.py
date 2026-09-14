import pathlib
from core.control_plane.jarvis import router as jarvis_router
import hashlib
import json
import os
import secrets
import sqlite3
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from fastapi.responses import FileResponse
from a1os_production_boundary import principal as a1os_principal, require as a1os_require, tenant_id as a1os_tenant_id, actor as a1os_actor, money as a1os_money, audit as a1os_audit, migrate as a1os_boundary_migrate
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "platform" / "a1os-platform-api" / "database" / "schema.sql"

DB_PATH = Path(
    os.getenv(
        "A1OS_PLATFORM_DB",
        str(
            ROOT
            / "runtime"
            / "a1os-platform-api"
            / "deployments"
            / "a1os-platform"
            / "data"
            / "a1os-platform.db"
        ),
    )
)


# ============================================================
# DATABASE
# ============================================================

def db():
    conn = sqlite3.connect(DB_PATH, timeout=30.0, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = db()

    try:
        schema = SCHEMA_PATH.read_text()
        conn.executescript(schema)
        conn.commit()

        # --------------------------------------------------------
        # Idempotent platform bootstrap
        #
        # Organization and administrator are reconciled
        # independently. An existing organization must never
        # prevent creation of a missing platform administrator.
        # --------------------------------------------------------

        org = conn.execute(
            "SELECT id FROM organizations WHERE code = 'a1os' LIMIT 1"
        ).fetchone()

        if org is None:
            conn.execute(
                """
                INSERT INTO organizations (code, name, industry)
                VALUES (?, ?, ?)
                """,
                ("a1os", "A1OS", "technology"),
            )
            conn.commit()

            org = conn.execute(
                "SELECT id FROM organizations WHERE code = 'a1os' LIMIT 1"
            ).fetchone()

        if org is None:
            raise RuntimeError(
                "A1OS bootstrap failed: platform organization could not be resolved"
            )

        org_id = org["id"]
        admin_email = os.getenv(
            "A1OS_PLATFORM_ADMIN_EMAIL",
            "admin@a1os.io",
        )

        admin = conn.execute(
            "SELECT id FROM users WHERE email = ? LIMIT 1",
            (admin_email,),
        ).fetchone()

        if admin is None:
            secret_path = pathlib.Path.home() / ".a1os" / "platform-admin-password"

            if not secret_path.exists():
                raise RuntimeError(
                    "Platform admin bootstrap secret is missing: "
                    f"{secret_path}"
                )

            admin_password = secret_path.read_text().strip()

            if not admin_password:
                raise RuntimeError(
                    "Platform admin bootstrap secret is empty"
                )

            conn.execute(
                """
                INSERT INTO users
                (organization_id, email, full_name, password_hash, role)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    org_id,
                    admin_email,
                    "A1OS Platform Administrator",
                    _hash_password(admin_password),
                    "super_admin",
                ),
            )
            conn.commit()

        else:
            # Existing administrator is preserved.
            # Bootstrap never rotates an existing password.
            conn.execute(
                """
                UPDATE users
                SET organization_id = ?,
                    role = 'super_admin',
                    active = 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (org_id, admin["id"]),
            )
            conn.commit()

    finally:
        conn.close()

# ============================================================
# PASSWORD HASHING
# ============================================================

def _hash_password(password: str) -> str:
    salt = secrets.token_bytes(16).hex()
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), PBKDF2_ITERATIONS
    )
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${dk.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        _, iters, salt, expected = stored.split("$")
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            bytes.fromhex(salt),
            int(iters),
        )
        return secrets.compare_digest(dk.hex(), expected)
    except Exception:
        return False


# ============================================================
# AUTH
# ============================================================

# ============================================================
# PLATFORM RUNTIME CONFIGURATION — v1.1
# ============================================================

A1OS_RUNTIME_ENV = os.getenv("A1OS_RUNTIME_ENV", "development")
A1OS_SERVICE_NAME = os.getenv("A1OS_SERVICE_NAME", "a1os-platform-api")
A1OS_READINESS_DB = os.getenv("A1OS_READINESS_DB", '/data/data/com.termux/files/home/A1OS_RESTORED/runtime/a1os-platform-api/deployments/a1os-platform/data/a1os-platform.db')
A1OS_COOKIE_SECURE = os.getenv("A1OS_COOKIE_SECURE", "false").lower() in ("1", "true", "yes", "on")

_LOGIN_ATTEMPTS = {}
_LOGIN_MAX_ATTEMPTS = 5
_LOGIN_WINDOW_SECONDS = 300
_AUTH_SESSION_DAYS = 7
PBKDF2_ITERATIONS = 200_000

RESERVED_ROLE_NAMES = {
    "super_admin",
    "admin",
    "platform_admin",
    "owner",
}

DEFAULT_ROLE_PERMISSIONS = {
    "super_admin": {"*"},
    "admin": {"*"},
    "platform_admin": {"*"},
    "owner": {"*"},
    "director": {
        "education:read",
        "education:write",
    },
    "manager": {
        "organizations:read",
        "organizations:write",
        "users:read",
        "users:write",
        "roles:read",
        "roles:write",
        "parties:read",
        "parties:write",
        "accounts:read",
        "products:read",
        "products:write",
        "inventory:read",
        "inventory:write",
        "ledger:read",
        "ledger:write",
        "audit:read",
        "notifications:read",
        "notifications:write",
    },
    "user": {
        "organizations:read",
        "users:read",
        "parties:read",
        "accounts:read",
        "products:read",
        "inventory:read",
        "ledger:read",
        "notifications:read",
    },
}


def _rate_limit_auth(request: Request):
    client = request.client.host if request.client else "unknown"
    now = time.monotonic()
    attempts = [
        ts for ts in _LOGIN_ATTEMPTS.get(client, [])
        if now - ts < _LOGIN_WINDOW_SECONDS
    ]
    if len(attempts) >= _LOGIN_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail="Too many authentication attempts. Try again later.",
        )
    _LOGIN_ATTEMPTS[client] = attempts


def _record_auth_attempt(client: str):
    now = time.monotonic()
    attempts = [
        ts for ts in _LOGIN_ATTEMPTS.get(client, [])
        if now - ts < _LOGIN_WINDOW_SECONDS
    ]
    attempts.append(now)
    _LOGIN_ATTEMPTS[client] = attempts


def _current_actor(request: Request):
    auth = request.headers.get("Authorization", "")
    token = ""

    if auth.startswith("Bearer "):
        token = auth[7:].strip()

    if not token:
        token = request.cookies.get("a1os_session", "").strip()

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    conn = db()
    try:
        row = conn.execute(
            """
            SELECT u.*, s.token AS session_token, s.expires_at AS session_expiry
            FROM auth_sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token = ?
            """,
            (token,),
        ).fetchone()
    finally:
        conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:
        expiry = datetime.fromisoformat(row["session_expiry"])
    except (TypeError, ValueError):
        expiry = datetime.min.replace(tzinfo=timezone.utc)

    if expiry < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")

    return dict(row)


def _permissions(conn, actor):
    override = conn.execute(
        """
        SELECT permissions
        FROM roles
        WHERE organization_id = ? AND name = ?
        """,
        (actor["organization_id"], actor["role"]),
    ).fetchone()
    if override:
        perms = json.loads(override["permissions"] or "[]")
        return set(perms)
    return set(DEFAULT_ROLE_PERMISSIONS.get(actor["role"], set()))


def _require_permission(request: Request, required: str):
    actor = _current_actor(request)
    conn = db()
    try:
        perms = _permissions(conn, actor)
    finally:
        conn.close()
    if "*" not in perms and required not in perms:
        raise HTTPException(
            status_code=403,
            detail=f"Missing permission: {required}",
        )
    return actor


def _audit(conn, actor, entity_type, entity_id, action, details=None):
    conn.execute(
        """
        INSERT INTO audit_log
        (organization_id, actor_user_id, entity_type, entity_id, action, details)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            actor["organization_id"],
            actor["id"],
            entity_type,
            entity_id,
            action,
            json.dumps(details or {}, default=str),
        ),
    )


# ============================================================
# PAGINATION HELPERS
# ============================================================

def _page_params(request, default_limit=None, max_limit=500):
    limit = default_limit
    raw_limit = request.query_params.get("limit")
    if raw_limit is not None:
        try:
            limit = int(raw_limit)
        except (TypeError, ValueError):
            limit = default_limit
    try:
        offset = int(request.query_params.get("offset", "0"))
    except (TypeError, ValueError):
        offset = 0
    if limit is not None:
        limit = max(0, min(limit, max_limit))
    offset = max(offset, 0)
    return limit, offset


def _pagination_sql(limit, offset):
    if limit is not None:
        return " LIMIT ? OFFSET ?", [limit, offset]
    if offset:
        return " OFFSET ?", [offset]
    return "", []


# ============================================================
# REALTIME CHANNELS
# ============================================================

WS_ROOMS = {}


async def _ws_send_to_org(organization_id, message):
    for ws in list(WS_ROOMS.get(organization_id, [])):
        try:
            await ws.send_json(message)
        except Exception:
            pass


# ============================================================
# APP
# ============================================================


a1os_boundary_migrate()


app = FastAPI(
    title="A1OS Platform API",
    version="1.0.0",
    description="Multi-tenant platform backend serving industry-specific frontends.",
)






# JARVIS Chat public static surface — intentionally mounted after FastAPI app creation.
app.mount("/jarvis-chat", StaticFiles(directory=str(Path(__file__).resolve().parents[4] / "products" / "verticals" / "jarvis-chat"), html=True), name="jarvis-chat")

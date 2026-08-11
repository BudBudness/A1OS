import hashlib
import json
import os
import secrets
import sqlite3
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[3]
DB_PATH = (
    ROOT
    / "products"
    / "a1os-platform-api"
    / "deployments"
    / "a1os-platform"
    / "data"
    / "a1os-platform.db"
)
SCHEMA_PATH = (
    ROOT / "products" / "a1os-platform-api" / "database" / "schema.sql"
)

AUTH_SESSION_DAYS = 30
LOGIN_MAX_ATTEMPTS = 20
LOGIN_WINDOW_SECONDS = 300
PBKDF2_ITERATIONS = 200_000

DEFAULT_ROLE_PERMISSIONS = {
    "super_admin": {"*"},
    "director": {"*"},
    "manager": {
        "dashboard.view",
        "parties.view",
        "parties.create",
        "products.view",
        "products.create",
        "ledger.view",
        "ledger.create",
        "inventory.view",
        "inventory.create",
        "notifications.view",
        "notifications.create",
        "audit.view",
    },
    "member": {"dashboard.view"},
}

RESERVED_ROLE_NAMES = {"super_admin", "director", "manager", "member"}


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
    schema = SCHEMA_PATH.read_text()
    conn.executescript(schema)
    conn.commit()

    org = conn.execute("SELECT id FROM organizations LIMIT 1").fetchone()
    if org is None:
        admin_email = os.getenv("A1OS_PLATFORM_ADMIN_EMAIL", "admin@a1os.io")
        secret_path = pathlib.Path.home() / ".a1os" / "platform-admin-password"
        if not secret_path.exists():
            raise RuntimeError(
                "Platform admin bootstrap secret is missing: "
                f"{secret_path}"
            )

        admin_password = secret_path.read_text().strip()
        if not admin_password:
            raise RuntimeError("Platform admin bootstrap secret is empty")
        conn.execute(
            """
            INSERT INTO organizations (code, name, industry)
            VALUES (?, ?, ?)
            """,
        )
        org_id = conn.execute(
            "SELECT id FROM organizations WHERE code = 'ICR'"
        ).fetchone()["id"]
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

_LOGIN_ATTEMPTS = {}


def _rate_limit_auth(request: Request):
    client = request.client.host if request.client else "unknown"
    now = time.monotonic()
    attempts = [
        ts for ts in _LOGIN_ATTEMPTS.get(client, [])
        if now - ts < LOGIN_WINDOW_SECONDS
    ]
    if len(attempts) >= LOGIN_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail="Too many authentication attempts. Try again later.",
        )
    _LOGIN_ATTEMPTS[client] = attempts


def _record_auth_attempt(client: str):
    now = time.monotonic()
    attempts = [
        ts for ts in _LOGIN_ATTEMPTS.get(client, [])
        if now - ts < LOGIN_WINDOW_SECONDS
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

app = FastAPI(
    title="A1OS Platform API",
    version="1.0.0",
    description="Multi-tenant platform backend serving industry-specific frontends.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    _init_db()


# ============================================================
# HEALTH
# ============================================================

@app.get("/v1/health")
def v1_health():
    return {"status": "ok", "service": "a1os-platform-api", "version": "1.0.0"}


def health():
    return {"status": "ok", "service": "a1os-platform-api", "version": "1.0.0"}


# ============================================================
# AUTHENTICATION
# ============================================================

@app.post("/v1/auth/login")
def auth_login(payload: dict, request: Request):
    _rate_limit_auth(request)

    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))

    if not email or not password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required",
        )

    conn = db()
    try:
        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE lower(email) = ? AND active = 1
            LIMIT 1
            """,
            (email,),
        ).fetchone()

        if not user or not _verify_password(password, user["password_hash"]):
            if request.client:
                _record_auth_attempt(request.client.host)
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            )

        token = secrets.token_urlsafe(48)
        expires_at = (
            datetime.now(timezone.utc) + timedelta(days=AUTH_SESSION_DAYS)
        ).isoformat()

        conn.execute(
            """
            INSERT INTO auth_sessions (user_id, token, expires_at)
            VALUES (?, ?, ?)
            """,
            (user["id"], token, expires_at),
        )
        _audit(conn, dict(user), "auth", user["id"], "login", {"email": email})

        perms = _permissions(conn, dict(user))

        response = JSONResponse({
            "status": "authenticated",
            "token": token,
            "expires_at": expires_at,
            "user": {
                "id": user["id"],
                "full_name": user["full_name"],
                "email": user["email"],
                "role": user["role"],
                "organization_id": user["organization_id"],
                "permissions": sorted(perms),
            },
        })

        response.set_cookie(
            key="a1os_session",
            value=token,
            httponly=True,
            secure=False,
            samesite="lax",
            path="/",
            max_age=60 * 60 * 24 * 30,
        )

        return response
    finally:
        conn.close()


@app.get("/v1/auth/me")
def auth_me(request: Request):
    actor = _current_actor(request)
    conn = db()
    try:
        perms = _permissions(conn, actor)
    finally:
        conn.close()
    return {
        "id": actor["id"],
        "full_name": actor["full_name"],
        "email": actor["email"],
        "role": actor["role"],
        "organization_id": actor["organization_id"],
        "permissions": sorted(perms),
    }


@app.post("/v1/auth/logout")
def auth_logout(request: Request):
    auth = request.headers.get("Authorization", "")
    token = ""

    if auth.startswith("Bearer "):
        token = auth[7:].strip()

    if not token:
        token = request.cookies.get("a1os_session", "").strip()

    if token:
        conn = db()
        try:
            conn.execute(
                "DELETE FROM auth_sessions WHERE token = ?",
                (token,),
            )
            conn.commit()
        finally:
            conn.close()

    response = JSONResponse({"status": "logged_out"})
    response.delete_cookie(
        key="a1os_session",
        path="/",
    )
    return response


@app.post("/v1/auth/change-password")
def auth_change_password(payload: dict, request: Request):
    actor = _current_actor(request)

    current = str(payload.get("current_password", ""))
    new_password = str(payload.get("new_password", ""))

    if not current or not new_password:
        raise HTTPException(
            status_code=400,
            detail="current_password and new_password are required",
        )
    if len(new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="new_password must be at least 8 characters",
        )

    conn = db()
    try:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE id = ?",
            (actor["id"],),
        ).fetchone()
        if not row or not _verify_password(current, row["password_hash"]):
            raise HTTPException(
                status_code=400,
                detail="Current password is incorrect",
            )
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (_hash_password(new_password), actor["id"]),
        )
        conn.execute(
            "DELETE FROM auth_sessions WHERE user_id = ?",
            (actor["id"],),
        )
        _audit(conn, actor, "user", actor["id"], "change_password", {})
        return {"status": "password_changed"}
    finally:
        conn.close()


# ============================================================
# ORGANIZATIONS
# ============================================================

@app.get("/v1/organizations")
def list_organizations(request: Request):
    actor = _current_actor(request)
    conn = db()
    try:
        if actor["role"] == "super_admin":
            rows = conn.execute(
                "SELECT * FROM organizations ORDER BY id"
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT * FROM organizations
                WHERE id = ?
                ORDER BY id
                """,
                (actor["organization_id"],),
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.post("/v1/organizations", status_code=201)
def create_organization(payload: dict, request: Request):
    actor = _current_actor(request)
    if actor["role"] != "super_admin":
        raise HTTPException(
            status_code=403,
            detail="Only super_admin may create organizations",
        )

    code = str(payload.get("code", "")).strip()
    name = str(payload.get("name", "")).strip()
    industry = str(payload.get("industry", "general")).strip()

    if not code or not name:
        raise HTTPException(
            status_code=422,
            detail="code and name are required",
        )

    conn = db()
    try:
        existing = conn.execute(
            "SELECT id FROM organizations WHERE code = ?",
            (code,),
        ).fetchone()
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Organization code already exists",
            )
        cur = conn.execute(
            """
            INSERT INTO organizations (code, name, industry)
            VALUES (?, ?, ?)
            """,
            (code, name, industry),
        )
        _audit(conn, actor, "organization", cur.lastrowid, "created",
               {"code": code, "name": name})
        return {
            "status": "created",
            "organization_id": cur.lastrowid,
        }
    finally:
        conn.close()


@app.patch("/v1/organizations/{organization_id}")
def update_organization(organization_id: int, payload: dict, request: Request):
    actor = _require_permission(request, "organizations.update")

    allowed = {"name", "industry"}
    updates = {k: v for k, v in payload.items() if k in allowed}
    if not updates:
        raise HTTPException(status_code=422, detail="No editable fields")

    conn = db()
    try:
        if actor["role"] != "super_admin":
            if organization_id != actor["organization_id"]:
                raise HTTPException(
                    status_code=404,
                    detail="Organization not found",
                )

        row = conn.execute(
            "SELECT id FROM organizations WHERE id = ?",
            (organization_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Organization not found")

        set_sql = ", ".join(f"{k} = ?" for k in updates)
        conn.execute(
            f"""
            UPDATE organizations
            SET {set_sql}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            list(updates.values()) + [organization_id],
        )
        _audit(conn, actor, "organization", organization_id, "updated",
               list(updates.keys()))
        return {"status": "updated", "organization_id": organization_id}
    finally:
        conn.close()


# ============================================================
# USERS
# ============================================================

@app.get("/v1/users")
def list_users(request: Request):
    actor = _require_permission(request, "users.view")
    limit, offset = _page_params(request)
    search = (request.query_params.get("search") or "").strip()

    conn = db()
    try:
        where = ["organization_id = ?"]
        params = [actor["organization_id"]]
        if search:
            like = f"%{search}%"
            where.append("(full_name LIKE ? OR email LIKE ?)")
            params.extend([like, like])

        where_sql = "WHERE " + " AND ".join(where)
        total = conn.execute(
            f"SELECT COUNT(*) AS total FROM users {where_sql}",
            params,
        ).fetchone()["total"]

        page_sql, page_params = _pagination_sql(limit, offset)
        rows = conn.execute(
            f"""
            SELECT id, full_name, email, role, active, created_at
            FROM users
            {where_sql}
            ORDER BY id DESC
            {page_sql}
            """,
            params + page_params,
        ).fetchall()

        return {
            "count": total,
            "limit": limit,
            "offset": offset,
            "users": [dict(r) for r in rows],
        }
    finally:
        conn.close()


@app.post("/v1/users", status_code=201)
def create_user(payload: dict, request: Request):
    actor = _require_permission(request, "users.create")

    email = str(payload.get("email", "")).strip().lower()
    full_name = str(payload.get("full_name", "")).strip()
    role = str(payload.get("role", "member")).strip()
    password = str(payload.get("password", ""))

    allowed_roles = set(DEFAULT_ROLE_PERMISSIONS.keys())
    if role not in allowed_roles:
        raise HTTPException(
            status_code=422,
            detail="Invalid role",
        )

    if role == "super_admin" and actor["role"] != "super_admin":
        raise HTTPException(
            status_code=403,
            detail="Only super_admin may assign super_admin",
        )

    if not email or not full_name or not password:
        raise HTTPException(
            status_code=422,
            detail="email, full_name, and password are required",
        )
    if len(password) < 8:
        raise HTTPException(
            status_code=422,
            detail="password must be at least 8 characters",
        )

    supplied_org = payload.get("organization_id")
    target_org_id = actor["organization_id"]
    if supplied_org is not None:
        try:
            supplied_org = int(supplied_org)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=422,
                detail="organization_id must be an integer",
            )
        if (
            actor["role"] != "super_admin"
            and supplied_org != actor["organization_id"]
        ):
            raise HTTPException(
                status_code=403,
                detail="Only super_admin may create users in another organization",
            )
        target_org_id = supplied_org

    conn = db()
    try:
        if target_org_id != actor["organization_id"]:
            org = conn.execute(
                "SELECT id FROM organizations WHERE id = ?",
                (target_org_id,),
            ).fetchone()
            if not org:
                raise HTTPException(
                    status_code=422,
                    detail="Organization not found",
                )

        existing = conn.execute(
            "SELECT id FROM users WHERE lower(email) = ?",
            (email,),
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")

        cur = conn.execute(
            """
            INSERT INTO users
            (organization_id, email, full_name, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                target_org_id,
                email,
                full_name,
                _hash_password(password),
                role,
            ),
        )
        _audit(conn, actor, "user", cur.lastrowid, "created", {"email": email})
        return {"status": "created", "user_id": cur.lastrowid}
    finally:
        conn.close()


@app.patch("/v1/users/{user_id}")
def update_user(user_id: int, payload: dict, request: Request):
    actor = _require_permission(request, "users.update")

    allowed = {"full_name", "role", "active"}
    updates = {k: v for k, v in payload.items() if k in allowed}
    if not updates:
        raise HTTPException(status_code=422, detail="No editable fields")

    if "role" in updates:
        requested_role = str(updates["role"]).strip()
        if requested_role not in DEFAULT_ROLE_PERMISSIONS:
            raise HTTPException(
                status_code=422,
                detail="Invalid role",
            )
        if requested_role == "super_admin" and actor["role"] != "super_admin":
            raise HTTPException(
                status_code=403,
                detail="Only super_admin may assign super_admin",
            )
        updates["role"] = requested_role

    conn = db()
    try:
        row = conn.execute(
            "SELECT id, role FROM users WHERE id = ? AND organization_id = ?",
            (user_id, actor["organization_id"]),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")

        if (
            actor["role"] != "super_admin"
            and row["role"] == "super_admin"
            and ("active" in updates or "role" in updates)
        ):
            raise HTTPException(
                status_code=403,
                detail="Only super_admin may modify a super_admin account",
            )

        set_sql = ", ".join(f"{k} = ?" for k in updates)
        conn.execute(
            f"""
            UPDATE users
            SET {set_sql}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            list(updates.values()) + [user_id],
        )
        _audit(conn, actor, "user", user_id, "updated", list(updates.keys()))
        return {"status": "updated", "user_id": user_id}
    finally:
        conn.close()


# ============================================================
# ROLES
# ============================================================

@app.get("/v1/roles")
def list_roles(request: Request):
    actor = _require_permission(request, "users.view")
    conn = db()
    try:
        rows = conn.execute(
            """
            SELECT id, name, permissions
            FROM roles
            WHERE organization_id = ?
            ORDER BY name
            """,
            (actor["organization_id"],),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.post("/v1/roles", status_code=201)
def create_role(payload: dict, request: Request):
    actor = _require_permission(request, "users.create")

    name = str(payload.get("name", "")).strip()
    perms = payload.get("permissions", [])

    if not name:
        raise HTTPException(status_code=422, detail="name is required")
    if name in RESERVED_ROLE_NAMES and actor["role"] != "super_admin":
        raise HTTPException(
            status_code=422,
            detail="Reserved role name cannot be used by tenants",
        )
    if not isinstance(perms, list):
        raise HTTPException(status_code=422, detail="permissions must be a list")

    if actor["role"] != "super_admin" and "*" in perms:
        raise HTTPException(
            status_code=403,
            detail="Platform wildcard permission is restricted to super_admin",
        )

    conn = db()
    try:
        cur = conn.execute(
            """
            INSERT INTO roles (organization_id, name, permissions)
            VALUES (?, ?, ?)
            """,
            (actor["organization_id"], name, json.dumps(perms)),
        )
        _audit(conn, actor, "role", cur.lastrowid, "created", {"name": name})
        return {"status": "created", "role_id": cur.lastrowid}
    finally:
        conn.close()


@app.patch("/v1/roles/{role_id}")
def update_role(role_id: int, payload: dict, request: Request):
    actor = _require_permission(request, "users.update")

    allowed = {"name", "permissions"}
    updates = {k: v for k, v in payload.items() if k in allowed}
    if not updates:
        raise HTTPException(status_code=422, detail="No editable fields")

    if "name" in updates:
        updates["name"] = str(updates["name"]).strip()
        if (
            updates["name"] in RESERVED_ROLE_NAMES
            and actor["role"] != "super_admin"
        ):
            raise HTTPException(
                status_code=422,
                detail="Reserved role name cannot be used by tenants",
            )

    conn = db()
    try:
        row = conn.execute(
            "SELECT id FROM roles WHERE id = ? AND organization_id = ?",
            (role_id, actor["organization_id"]),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Role not found")

        if "permissions" in updates:
            if not isinstance(updates["permissions"], list):
                raise HTTPException(
                    status_code=422,
                    detail="permissions must be a list",
                )
            if actor["role"] != "super_admin" and "*" in updates["permissions"]:
                raise HTTPException(
                    status_code=403,
                    detail="Platform wildcard permission is restricted to super_admin",
                )
            updates["permissions"] = json.dumps(updates["permissions"])

        set_sql = ", ".join(f"{k} = ?" for k in updates)
        conn.execute(
            f"""
            UPDATE roles
            SET {set_sql}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            list(updates.values()) + [role_id],
        )
        _audit(conn, actor, "role", role_id, "updated", list(updates.keys()))
        return {"status": "updated", "role_id": role_id}
    finally:
        conn.close()


# ============================================================
# PARTIES (customers / suppliers / farmers / buyers)
# ============================================================

@app.get("/v1/parties")
def list_parties(request: Request):
    actor = _require_permission(request, "parties.view")
    limit, offset = _page_params(request)
    search = (request.query_params.get("search") or "").strip()
    party_type = (request.query_params.get("party_type") or "").strip()

    conn = db()
    try:
        where = ["organization_id = ?"]
        params = [actor["organization_id"]]
        if party_type:
            where.append("party_type = ?")
            params.append(party_type)
        if search:
            like = f"%{search}%"
            where.append("(name LIKE ? OR phone LIKE ? OR email LIKE ?)")
            params.extend([like, like, like])

        where_sql = "WHERE " + " AND ".join(where)
        total = conn.execute(
            f"SELECT COUNT(*) AS total FROM parties {where_sql}",
            params,
        ).fetchone()["total"]

        page_sql, page_params = _pagination_sql(limit, offset)
        rows = conn.execute(
            f"""
            SELECT *
            FROM parties
            {where_sql}
            ORDER BY id DESC
            {page_sql}
            """,
            params + page_params,
        ).fetchall()

        return {
            "count": total,
            "limit": limit,
            "offset": offset,
            "parties": [dict(r) for r in rows],
        }
    finally:
        conn.close()


@app.post("/v1/parties", status_code=201)
def create_party(payload: dict, request: Request):
    actor = _require_permission(request, "parties.create")

    name = str(payload.get("name", "")).strip()
    party_type = str(payload.get("party_type", "customer")).strip()

    if not name:
        raise HTTPException(status_code=422, detail="name is required")
    if party_type not in {"customer", "supplier", "farmer", "buyer"}:
        raise HTTPException(
            status_code=422,
            detail="party_type must be customer, supplier, farmer, or buyer",
        )

    conn = db()
    try:
        cur = conn.execute(
            """
            INSERT INTO parties
            (organization_id, party_type, name, phone, email, location, external_ref)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                actor["organization_id"],
                party_type,
                name,
                payload.get("phone"),
                payload.get("email"),
                payload.get("location"),
                payload.get("external_ref"),
            ),
        )
        _audit(conn, actor, "party", cur.lastrowid, "created",
               {"name": name, "party_type": party_type})
        return {"status": "created", "party_id": cur.lastrowid}
    finally:
        conn.close()


@app.patch("/v1/parties/{party_id}")
def update_party(party_id: int, payload: dict, request: Request):
    actor = _require_permission(request, "parties.update")

    allowed = {
        "party_type", "name", "phone", "email", "location", "external_ref",
    }
    updates = {k: v for k, v in payload.items() if k in allowed}
    if not updates:
        raise HTTPException(status_code=422, detail="No editable fields")

    conn = db()
    try:
        row = conn.execute(
            "SELECT id FROM parties WHERE id = ? AND organization_id = ?",
            (party_id, actor["organization_id"]),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Party not found")

        set_sql = ", ".join(f"{k} = ?" for k in updates)
        conn.execute(
            f"""
            UPDATE parties
            SET {set_sql}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            list(updates.values()) + [party_id],
        )
        _audit(conn, actor, "party", party_id, "updated", list(updates.keys()))
        return {"status": "updated", "party_id": party_id}
    finally:
        conn.close()


# ============================================================
# PRODUCTS
# ============================================================

@app.get("/v1/products")
def list_products(request: Request):
    actor = _require_permission(request, "products.view")
    limit, offset = _page_params(request)
    search = (request.query_params.get("search") or "").strip()

    conn = db()
    try:
        where = ["organization_id = ?"]
        params = [actor["organization_id"]]
        if search:
            like = f"%{search}%"
            where.append("(name LIKE ? OR sku LIKE ? OR category LIKE ?)")
            params.extend([like, like, like])

        where_sql = "WHERE " + " AND ".join(where)
        total = conn.execute(
            f"SELECT COUNT(*) AS total FROM products {where_sql}",
            params,
        ).fetchone()["total"]

        page_sql, page_params = _pagination_sql(limit, offset)
        rows = conn.execute(
            f"""
            SELECT *
            FROM products
            {where_sql}
            ORDER BY id DESC
            {page_sql}
            """,
            params + page_params,
        ).fetchall()

        return {
            "count": total,
            "limit": limit,
            "offset": offset,
            "products": [dict(r) for r in rows],
        }
    finally:
        conn.close()


@app.post("/v1/products", status_code=201)
def create_product(payload: dict, request: Request):
    actor = _require_permission(request, "products.create")

    name = str(payload.get("name", "")).strip()
    sku = str(payload.get("sku", "")).strip()

    if not name or not sku:
        raise HTTPException(status_code=422, detail="name and sku are required")

    conn = db()
    try:
        existing = conn.execute(
            "SELECT id FROM products WHERE sku = ?",
            (sku,),
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="SKU already exists")

        cur = conn.execute(
            """
            INSERT INTO products
            (organization_id, name, sku, category, unit, cost_price, selling_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                actor["organization_id"],
                name,
                sku,
                payload.get("category"),
                str(payload.get("unit", "kg")),
                payload.get("cost_price"),
                payload.get("selling_price"),
            ),
        )
        _audit(conn, actor, "product", cur.lastrowid, "created",
               {"name": name, "sku": sku})
        return {"status": "created", "product_id": cur.lastrowid}
    finally:
        conn.close()


@app.patch("/v1/products/{product_id}")
def update_product(product_id: int, payload: dict, request: Request):
    actor = _require_permission(request, "products.update")

    allowed = {
        "name", "category", "unit", "cost_price", "selling_price", "active",
    }
    updates = {k: v for k, v in payload.items() if k in allowed}
    if not updates:
        raise HTTPException(status_code=422, detail="No editable fields")

    conn = db()
    try:
        row = conn.execute(
            "SELECT id FROM products WHERE id = ? AND organization_id = ?",
            (product_id, actor["organization_id"]),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Product not found")

        set_sql = ", ".join(f"{k} = ?" for k in updates)
        conn.execute(
            f"""
            UPDATE products
            SET {set_sql}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            list(updates.values()) + [product_id],
        )
        _audit(conn, actor, "product", product_id, "updated",
               list(updates.keys()))
        return {"status": "updated", "product_id": product_id}
    finally:
        conn.close()


# ============================================================
# ACCOUNTS
# ============================================================

@app.get("/v1/accounts")
def list_accounts(request: Request):
    actor = _require_permission(request, "ledger.view")
    account_type = (request.query_params.get("account_type") or "").strip()

    conn = db()
    try:
        if account_type:
            rows = conn.execute(
                """
                SELECT * FROM accounts
                WHERE organization_id = ? AND account_type = ?
                ORDER BY name
                """,
                (actor["organization_id"], account_type),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT * FROM accounts
                WHERE organization_id = ?
                ORDER BY name
                """,
                (actor["organization_id"],),
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.post("/v1/accounts", status_code=201)
def create_account(payload: dict, request: Request):
    actor = _require_permission(request, "ledger.create")

    name = str(payload.get("name", "")).strip()
    account_type = str(payload.get("account_type", "")).strip()

    valid_types = {
        "asset", "liability", "revenue", "expense", "equity",
        "receivable", "payable",
    }
    if not name or not account_type:
        raise HTTPException(
            status_code=422,
            detail="name and account_type are required",
        )
    if account_type not in valid_types:
        raise HTTPException(
            status_code=422,
            detail=f"account_type must be one of: {sorted(valid_types)}",
        )

    conn = db()
    try:
        cur = conn.execute(
            """
            INSERT INTO accounts (organization_id, account_type, name, party_id)
            VALUES (?, ?, ?, ?)
            """,
            (
                actor["organization_id"],
                account_type,
                name,
                payload.get("party_id"),
            ),
        )
        _audit(conn, actor, "account", cur.lastrowid, "created",
               {"name": name, "account_type": account_type})
        return {"status": "created", "account_id": cur.lastrowid}
    finally:
        conn.close()


# ============================================================
# LEDGER (double-entry)
# ============================================================

@app.post("/v1/ledger", status_code=201)
def create_ledger_entry(payload: dict, request: Request):
    actor = _require_permission(request, "ledger.create")

    entry_date = str(payload.get("entry_date", "")).strip()
    description = str(payload.get("description", "")).strip()
    debit_account_id = payload.get("debit_account_id")
    credit_account_id = payload.get("credit_account_id")
    reference = str(payload.get("reference", "")).strip()

    try:
        amount = float(payload.get("amount"))
    except (TypeError, ValueError):
        amount = None

    if not entry_date or amount is None:
        raise HTTPException(
            status_code=422,
            detail="entry_date and amount are required",
        )
    if amount <= 0:
        raise HTTPException(status_code=422, detail="amount must be positive")
    if not debit_account_id or not credit_account_id:
        raise HTTPException(
            status_code=422,
            detail="debit_account_id and credit_account_id are required",
        )
    if debit_account_id == credit_account_id:
        raise HTTPException(
            status_code=422,
            detail="debit and credit accounts must differ",
        )

    conn = db()
    try:
        accounts = conn.execute(
            """
            SELECT id FROM accounts
            WHERE organization_id = ? AND id IN (?, ?)
            """,
            (actor["organization_id"], debit_account_id, credit_account_id),
        ).fetchall()
        if len(accounts) != 2:
            raise HTTPException(
                status_code=422,
                detail="Both accounts must belong to the organization",
            )

        cur = conn.execute(
            """
            INSERT INTO ledger_entries
            (organization_id, entry_date, description,
             debit_account_id, credit_account_id, amount, reference, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                actor["organization_id"],
                entry_date,
                description,
                debit_account_id,
                credit_account_id,
                amount,
                reference,
                actor["id"],
            ),
        )
        _audit(conn, actor, "ledger", cur.lastrowid, "created",
               {"amount": amount, "reference": reference})
        return {"status": "created", "entry_id": cur.lastrowid}
    finally:
        conn.close()


@app.get("/v1/ledger")
def list_ledger(request: Request):
    actor = _require_permission(request, "ledger.view")
    limit, offset = _page_params(request)

    conn = db()
    try:
        where = ["l.organization_id = ?"]
        params = [actor["organization_id"]]

        where_sql = "WHERE " + " AND ".join(where)
        total = conn.execute(
            f"SELECT COUNT(*) AS total FROM ledger_entries l {where_sql}",
            params,
        ).fetchone()["total"]

        page_sql, page_params = _pagination_sql(limit, offset)
        rows = conn.execute(
            f"""
            SELECT
                l.*,
                da.name AS debit_account_name,
                ca.name AS credit_account_name
            FROM ledger_entries l
            LEFT JOIN accounts da ON da.id = l.debit_account_id
            LEFT JOIN accounts ca ON ca.id = l.credit_account_id
            {where_sql}
            ORDER BY l.entry_date DESC, l.id DESC
            {page_sql}
            """,
            params + page_params,
        ).fetchall()

        return {
            "count": total,
            "limit": limit,
            "offset": offset,
            "entries": [dict(r) for r in rows],
        }
    finally:
        conn.close()


@app.get("/v1/ledger/balances")
def ledger_balances(request: Request):
    actor = _require_permission(request, "ledger.view")
    account_id = request.query_params.get("account_id")

    conn = db()
    try:
        if account_id:
            rows = conn.execute(
                """
                SELECT
                    a.id AS account_id,
                    a.name,
                    a.account_type,
                    COALESCE(SUM(
                        CASE WHEN l.debit_account_id = a.id THEN l.amount ELSE 0 END
                    ), 0) AS total_debits,
                    COALESCE(SUM(
                        CASE WHEN l.credit_account_id = a.id THEN l.amount ELSE 0 END
                    ), 0) AS total_credits,
                    COALESCE(SUM(
                        CASE WHEN l.debit_account_id = a.id THEN l.amount
                             WHEN l.credit_account_id = a.id THEN -l.amount
                             ELSE 0 END
                    ), 0) AS net_balance
                FROM accounts a
                LEFT JOIN ledger_entries l
                    ON l.organization_id = a.organization_id
                    AND (l.debit_account_id = a.id OR l.credit_account_id = a.id)
                WHERE a.id = ? AND a.organization_id = ?
                GROUP BY a.id
                """,
                (int(account_id), actor["organization_id"]),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT
                    a.id AS account_id,
                    a.name,
                    a.account_type,
                    COALESCE(SUM(
                        CASE WHEN l.debit_account_id = a.id THEN l.amount ELSE 0 END
                    ), 0) AS total_debits,
                    COALESCE(SUM(
                        CASE WHEN l.credit_account_id = a.id THEN l.amount ELSE 0 END
                    ), 0) AS total_credits,
                    COALESCE(SUM(
                        CASE WHEN l.debit_account_id = a.id THEN l.amount
                             WHEN l.credit_account_id = a.id THEN -l.amount
                             ELSE 0 END
                    ), 0) AS net_balance
                FROM accounts a
                LEFT JOIN ledger_entries l
                    ON l.organization_id = a.organization_id
                    AND (l.debit_account_id = a.id OR l.credit_account_id = a.id)
                WHERE a.organization_id = ?
                GROUP BY a.id
                ORDER BY a.name
                """,
                (actor["organization_id"],),
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/v1/ledger/trial-balance")
def ledger_trial_balance(request: Request):
    actor = _require_permission(request, "ledger.view")

    conn = db()
    try:
        row = conn.execute(
            """
            SELECT
                COALESCE(SUM(amount), 0) AS total_debits,
                COALESCE(SUM(amount), 0) AS total_credits,
                COUNT(*) AS entries
            FROM ledger_entries
            WHERE organization_id = ?
            """,
            (actor["organization_id"],),
        ).fetchone()

        return {
            "total_debits": round(float(row["total_debits"]), 2),
            "total_credits": round(float(row["total_credits"]), 2),
            "balanced": float(row["total_debits"]) == float(row["total_credits"]),
            "entries": row["entries"],
        }
    finally:
        conn.close()


# ============================================================
# INVENTORY / WAREHOUSE
# ============================================================

@app.get("/v1/inventory/items")
def list_inventory(request: Request):
    actor = _require_permission(request, "inventory.view")
    limit, offset = _page_params(request)
    warehouse = (request.query_params.get("warehouse") or "").strip()

    conn = db()
    try:
        where = ["si.organization_id = ?"]
        params = [actor["organization_id"]]
        if warehouse:
            where.append("si.warehouse = ?")
            params.append(warehouse)

        where_sql = "WHERE " + " AND ".join(where)
        total = conn.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM stock_items si
            {where_sql}
            """,
            params,
        ).fetchone()["total"]

        page_sql, page_params = _pagination_sql(limit, offset)
        rows = conn.execute(
            f"""
            SELECT
                si.id,
                si.product_id,
                p.name AS product_name,
                p.sku,
                p.unit,
                si.warehouse,
                si.quantity,
                si.unit_cost,
                si.updated_at
            FROM stock_items si
            JOIN products p ON p.id = si.product_id
            {where_sql}
            ORDER BY p.name, si.warehouse
            {page_sql}
            """,
            params + page_params,
        ).fetchall()

        return {
            "count": total,
            "limit": limit,
            "offset": offset,
            "items": [dict(r) for r in rows],
        }
    finally:
        conn.close()


@app.post("/v1/inventory/movements", status_code=201)
def create_stock_movement(payload: dict, request: Request):
    actor = _require_permission(request, "inventory.create")

    product_id = payload.get("product_id")
    warehouse = str(payload.get("warehouse", "main")).strip()
    movement_type = str(payload.get("movement_type", "")).strip()
    reference = str(payload.get("reference", "")).strip()

    try:
        quantity = float(payload.get("quantity"))
    except (TypeError, ValueError):
        quantity = None

    if not product_id or quantity is None:
        raise HTTPException(
            status_code=422,
            detail="product_id and quantity are required",
        )
    if quantity <= 0:
        raise HTTPException(status_code=422, detail="quantity must be positive")
    if movement_type not in {"receipt", "issue", "adjustment"}:
        raise HTTPException(
            status_code=422,
            detail="movement_type must be receipt, issue, or adjustment",
        )

    conn = db()
    try:
        product = conn.execute(
            """
            SELECT id FROM products
            WHERE id = ? AND organization_id = ?
            """,
            (product_id, actor["organization_id"]),
        ).fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        item = conn.execute(
            """
            SELECT id, quantity FROM stock_items
            WHERE organization_id = ? AND product_id = ? AND warehouse = ?
            """,
            (actor["organization_id"], product_id, warehouse),
        ).fetchone()

        if item is None:
            cur = conn.execute(
                """
                INSERT INTO stock_items
                (organization_id, product_id, warehouse, quantity, unit_cost)
                VALUES (?, ?, ?, 0, ?)
                """,
                (
                    actor["organization_id"],
                    product_id,
                    warehouse,
                    payload.get("unit_cost"),
                ),
            )
            item_id = cur.lastrowid
            current_qty = 0.0
        else:
            item_id = item["id"]
            current_qty = float(item["quantity"])

        if movement_type == "receipt":
            new_qty = current_qty + quantity
        elif movement_type == "issue":
            new_qty = current_qty - quantity
        else:
            new_qty = quantity

        if new_qty < 0:
            raise HTTPException(
                status_code=422,
                detail="Movement would drive stock negative",
            )

        conn.execute(
            """
            INSERT INTO stock_movements
            (organization_id, product_id, warehouse, movement_type,
             quantity, reference, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                actor["organization_id"],
                product_id,
                warehouse,
                movement_type,
                quantity,
                reference,
                actor["id"],
            ),
        )
        conn.execute(
            """
            UPDATE stock_items
            SET quantity = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (new_qty, item_id),
        )
        _audit(conn, actor, "stock", item_id, movement_type,
               {"product_id": product_id, "quantity": quantity})
        return {
            "status": "recorded",
            "item_id": item_id,
            "quantity": new_qty,
        }
    finally:
        conn.close()


@app.get("/v1/inventory/movements")
def list_stock_movements(request: Request):
    actor = _require_permission(request, "inventory.view")
    limit, offset = _page_params(request)

    conn = db()
    try:
        page_sql, page_params = _pagination_sql(limit, offset)
        rows = conn.execute(
            f"""
            SELECT
                m.*,
                p.name AS product_name,
                p.sku
            FROM stock_movements m
            JOIN products p ON p.id = m.product_id
            WHERE m.organization_id = ?
            ORDER BY m.id DESC
            {page_sql}
            """,
            [actor["organization_id"]] + page_params,
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ============================================================
# NOTIFICATIONS
# ============================================================

@app.get("/v1/notifications")
def list_notifications(request: Request):
    actor = _require_permission(request, "notifications.view")
    limit, offset = _page_params(request)
    status_filter = (request.query_params.get("status") or "").strip()

    conn = db()
    try:
        where = ["organization_id = ?"]
        params = [actor["organization_id"]]
        if status_filter:
            where.append("status = ?")
            params.append(status_filter)

        where_sql = "WHERE " + " AND ".join(where)
        total = conn.execute(
            f"SELECT COUNT(*) AS total FROM notifications {where_sql}",
            params,
        ).fetchone()["total"]

        page_sql, page_params = _pagination_sql(limit, offset)
        rows = conn.execute(
            f"""
            SELECT *
            FROM notifications
            {where_sql}
            ORDER BY id DESC
            {page_sql}
            """,
            params + page_params,
        ).fetchall()

        return {
            "count": total,
            "limit": limit,
            "offset": offset,
            "notifications": [dict(r) for r in rows],
        }
    finally:
        conn.close()


@app.post("/v1/notifications", status_code=201)
def create_notification(payload: dict, request: Request):
    actor = _require_permission(request, "notifications.create")

    subject = str(payload.get("subject", "")).strip()
    body = str(payload.get("body", "")).strip()

    if not subject:
        raise HTTPException(status_code=422, detail="subject is required")

    conn = db()
    try:
        cur = conn.execute(
            """
            INSERT INTO notifications
            (organization_id, channel, recipient, subject, body, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                actor["organization_id"],
                str(payload.get("channel", "inapp")),
                payload.get("recipient"),
                subject,
                body,
                str(payload.get("status", "pending")),
            ),
        )
        _audit(conn, actor, "notification", cur.lastrowid, "created",
               {"subject": subject})
        return {"status": "created", "notification_id": cur.lastrowid}
    finally:
        conn.close()


# ============================================================
# AUDIT
# ============================================================

@app.get("/v1/audit")
def list_audit_logs(request: Request):
    actor = _require_permission(request, "audit.view")
    limit, offset = _page_params(request, default_limit=100)
    search = (request.query_params.get("search") or "").strip()

    conn = db()
    try:
        where = ["a.organization_id = ?"]
        params = [actor["organization_id"]]
        if search:
            like = f"%{search}%"
            where.append("(a.entity_type LIKE ? OR a.action LIKE ? OR u.full_name LIKE ?)")
            params.extend([like, like, like])

        where_sql = "WHERE " + " AND ".join(where)
        page_sql, page_params = _pagination_sql(limit, offset)
        rows = conn.execute(
            f"""
            SELECT
                a.*,
                u.full_name AS actor_name,
                u.email AS actor_email
            FROM audit_log a
            LEFT JOIN users u ON u.id = a.actor_user_id
            {where_sql}
            ORDER BY a.id DESC
            {page_sql}
            """,
            params + page_params,
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ============================================================
# REALTIME WEBSOCKET
# ============================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token", "")
    conn = db()
    try:
        row = conn.execute(
            """
            SELECT u.*, s.expires_at AS session_expiry
            FROM auth_sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token = ?
            """,
            (token,),
        ).fetchone()
    finally:
        conn.close()

    if not row:
        await websocket.close(code=4401)
        return

    try:
        expiry = datetime.fromisoformat(row["session_expiry"])
    except (TypeError, ValueError):
        expiry = datetime.min.replace(tzinfo=timezone.utc)
    if expiry < datetime.now(timezone.utc):
        await websocket.close(code=4401)
        return

    organization_id = row["organization_id"]

    await websocket.accept()
    WS_ROOMS.setdefault(organization_id, []).append(websocket)

    await websocket.send_json({
        "type": "connected",
        "organization_id": organization_id,
    })

    try:
        while True:
            message = await websocket.receive_json()
            if isinstance(message, dict) and message.get("type") == "broadcast":
                payload = message.get("payload", {})
                await _ws_send_to_org(organization_id, {
                    "type": "event",
                    "source": row["email"],
                    "payload": payload,
                })
    except WebSocketDisconnect:
        pass
    finally:
        room = WS_ROOMS.get(organization_id, [])
        if websocket in room:
            room.remove(websocket)

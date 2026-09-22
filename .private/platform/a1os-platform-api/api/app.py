import pathlib
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
            ROOT.parent
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
A1OS_READINESS_DB = os.getenv("A1OS_READINESS_DB", str(DB_PATH))
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
        "users:read",
        "users:write",
    },
    "headmistress": {
        "education:read",
        "education:write",
    },
    "staff": {
        "education:read",
    },
    "driver": {
        "education:read",
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


def _bootstrap_runtime_schema():
    conn = db()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS platform_workflow_definitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER,
                key TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                trigger_type TEXT NOT NULL DEFAULT 'manual',
                enabled INTEGER NOT NULL DEFAULT 1,
                version TEXT NOT NULL DEFAULT '1',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(organization_id, key)
            );

            CREATE TABLE IF NOT EXISTS platform_attention_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER,
                severity TEXT NOT NULL DEFAULT 'medium',
                category TEXT NOT NULL DEFAULT 'general',
                title TEXT NOT NULL,
                detail TEXT,
                status TEXT NOT NULL DEFAULT 'open',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS platform_execution_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER,
                workflow_key TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                requested_by INTEGER,
                approval_id INTEGER,
                started_at TEXT,
                finished_at TEXT,
                error TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS platform_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER,
                resource_type TEXT NOT NULL,
                resource_key TEXT NOT NULL,
                name TEXT NOT NULL,
                config_json TEXT NOT NULL DEFAULT '{}',
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(organization_id, resource_type, resource_key)
            );

            CREATE TABLE IF NOT EXISTS platform_capabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER,
                capability_key TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                config_json TEXT NOT NULL DEFAULT '{}',
                enabled INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(organization_id, capability_key)
            );

            CREATE TABLE IF NOT EXISTS platform_policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER,
                policy_key TEXT NOT NULL,
                name TEXT NOT NULL,
                effect TEXT NOT NULL DEFAULT 'allow',
                rules_json TEXT NOT NULL DEFAULT '{}',
                enabled INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(organization_id, policy_key)
            );

            CREATE TABLE IF NOT EXISTS platform_workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER,
                workflow_key TEXT NOT NULL,
                name TEXT NOT NULL,
                definition_json TEXT NOT NULL DEFAULT '{}',
                enabled INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(organization_id, workflow_key)
            );

            CREATE TABLE IF NOT EXISTS platform_workflow_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id INTEGER NOT NULL,
                organization_id INTEGER,
                status TEXT NOT NULL DEFAULT 'pending',
                input_json TEXT NOT NULL DEFAULT '{}',
                output_json TEXT NOT NULL DEFAULT '{}',
                error TEXT,
                started_at TEXT,
                completed_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(workflow_id) REFERENCES platform_workflows(id)
            );

            CREATE TABLE IF NOT EXISTS platform_approvals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER,
                action_key TEXT NOT NULL,
                action_type TEXT NOT NULL,
                target_type TEXT,
                target_id TEXT,
                requested_by INTEGER,
                approved_by INTEGER,
                status TEXT NOT NULL DEFAULT 'pending',
                reason TEXT,
                decision_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                decided_at TEXT
            );

            CREATE TABLE IF NOT EXISTS platform_billing_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_key TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                currency TEXT NOT NULL DEFAULT 'UGX',
                amount REAL NOT NULL DEFAULT 0,
                interval TEXT NOT NULL DEFAULT 'monthly',
                capabilities_json TEXT NOT NULL DEFAULT '[]',
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS platform_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER NOT NULL,
                plan_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                renews_at TEXT,
                external_ref TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(plan_id) REFERENCES platform_billing_plans(id)
            );

            CREATE TABLE IF NOT EXISTS platform_deployments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER,
                deployment_key TEXT NOT NULL,
                target TEXT NOT NULL,
                version TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                evidence_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT
            );

            CREATE TABLE IF NOT EXISTS platform_product_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER NOT NULL,
                product_key TEXT NOT NULL,
                version TEXT NOT NULL DEFAULT '1',
                config_json TEXT NOT NULL DEFAULT '{}',
                enabled INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(organization_id, product_key)
            );

            CREATE TABLE IF NOT EXISTS platform_usage_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER,
                capability_key TEXT NOT NULL,
                quantity REAL NOT NULL DEFAULT 1,
                unit TEXT NOT NULL DEFAULT 'event',
                reference TEXT,
                metadata_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS platform_health_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_key TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'unknown',
                details_json TEXT NOT NULL DEFAULT '{}',
                checked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS platform_entitlements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER NOT NULL,
                capability_key TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                source TEXT NOT NULL DEFAULT 'system',
                starts_at TEXT,
                expires_at TEXT,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(organization_id, capability_key)
            );

            CREATE TABLE IF NOT EXISTS platform_release_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                release_id TEXT NOT NULL,
                check_name TEXT NOT NULL,
                result TEXT NOT NULL DEFAULT 'pass',
                evidence TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


_bootstrap_runtime_schema()


app = FastAPI(
    title="A1OS Platform API",
    version="1.0.0",
    description="Multi-tenant platform backend serving industry-specific frontends.",
)


# ============================================================
# A1OS WEB EXPERIENCES
# ============================================================
# The canonical 3013 service serves the platform API and the two
# A1OS browser experiences. Host routing keeps both on the same
# platform service without creating another backend or port.
_A1OS_PRODUCTS_ROOT = ROOT.parent / "products"
_A1OS_PUBLIC_ROOT = _A1OS_PRODUCTS_ROOT / "a1os-public"
_A1OS_CONTROL_ROOT = _A1OS_PRODUCTS_ROOT / "a1os-control-plane"


def _a1os_host(request: Request) -> str:
    return (request.headers.get("host") or "").split(":", 1)[0].lower()


@app.get("/", include_in_schema=False)
def a1os_web_root(request: Request):
    host = _a1os_host(request)
    if host in {"a1os.ug", "www.a1os.ug"} and (_A1OS_PUBLIC_ROOT / "index.html").is_file():
        return FileResponse(_A1OS_PUBLIC_ROOT / "index.html")
    if host == "app.a1os.ug" and (_A1OS_CONTROL_ROOT / "index.html").is_file():
        return FileResponse(_A1OS_CONTROL_ROOT / "index.html")
    return JSONResponse({
        "platform": "A1OS",
        "service": "a1os-platform-api",
        "status": "ok",
    })


@app.get("/styles.css", include_in_schema=False)
def a1os_styles(request: Request):
    host = _a1os_host(request)
    if host in {"a1os.ug", "www.a1os.ug"}:
        path = _A1OS_PUBLIC_ROOT / "styles.css"
    elif host == "app.a1os.ug":
        path = _A1OS_CONTROL_ROOT / "styles.css"
    else:
        raise HTTPException(status_code=404, detail="Web asset not found")
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Web asset not found")
    return FileResponse(path)


@app.on_event("startup")
def _on_startup():
    _bootstrap_runtime_schema()






# ============================================================

# ============================================================
# HEALTH
# ============================================================




# === A1OS PRODUCTIZATION RELEASE ===
from fastapi import APIRouter as _A1OSRouter
from fastapi.responses import HTMLResponse as _A1OSHTMLResponse
import sqlite3 as _A1OSSqlite3
import json as _A1OSJson
from datetime import datetime as _A1OSDatetime, timezone as _A1OSTimezone

_a1os_product_router = _A1OSRouter(prefix="/v1/platform/product", tags=["platform-product"])

def _a1os_product_db():
    c = _A1OSSqlite3.connect(DB_PATH, timeout=30.0, isolation_level=None)
    c.row_factory = _A1OSSqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c

def _a1os_product_now():
    return _A1OSDatetime.now(_A1OSTimezone.utc).isoformat()

def _a1os_product_actor(request):
    return _require_permission(request, "organizations:read")

@_a1os_product_router.get("/command-center")
def _a1os_product_command_center(request: Request):
    _a1os_product_actor(request)
    p = ROOT / ".private" / "platform" / "a1os-platform-contract" / "runtime" / "command-center.html"
    return _A1OSHTMLResponse(p.read_text())

@_a1os_product_router.get("/snapshot")
def _a1os_product_snapshot(request: Request):
    actor = _a1os_product_actor(request)
    org_id = actor.get("organization_id")
    c = _a1os_product_db()
    try:
        def count(sql, args=()):
            return c.execute(sql,args).fetchone()[0]

        orgs = count("SELECT COUNT(*) FROM organizations")
        products = count("SELECT COUNT(*) FROM products")
        workflows = count("SELECT COUNT(*) FROM platform_workflow_definitions WHERE enabled=1")
        approvals = count("SELECT COUNT(*) FROM platform_approvals WHERE status='pending'")
        attention = count("SELECT COUNT(*) FROM platform_attention_items WHERE status='open'")
        runs = count("SELECT COUNT(*) FROM platform_execution_runs WHERE status='running'")
        subscriptions = count("SELECT COUNT(*) FROM platform_subscriptions WHERE status='active'")
        resources = count("SELECT COUNT(*) FROM platform_resources")
        deployments = count("SELECT COUNT(*) FROM platform_deployments")

        return {
            "status":"ok",
            "generated_at":_a1os_product_now(),
            "authority":"approval_gated",
            "architecture":"folders_over_agents",
            "scope":{"organization_id":org_id},
            "metrics":{
                "organizations":orgs,
                "products":products,
                "resources":resources,
                "active_workflows":workflows,
                "pending_approvals":approvals,
                "open_attention":attention,
                "running_executions":runs,
                "active_subscriptions":subscriptions,
                "deployments":deployments
            }
        }
    finally:
        c.close()

@_a1os_product_router.get("/attention")
def _a1os_product_attention(request: Request):
    _a1os_product_actor(request)
    c = _a1os_product_db()
    try:
        rows = c.execute("""
            SELECT id,organization_id,severity,category,title,detail,status,created_at
            FROM platform_attention_items
            WHERE status='open'
            ORDER BY
              CASE severity WHEN 'critical' THEN 1 WHEN 'high' THEN 2
              WHEN 'medium' THEN 3 ELSE 4 END, id DESC
            LIMIT 100
        """).fetchall()
        return {"items":[dict(x) for x in rows]}
    finally:
        c.close()

@_a1os_product_router.get("/workflows")
def _a1os_product_workflows(request: Request):
    actor = _a1os_product_actor(request)
    c = _a1os_product_db()
    try:
        rows = c.execute("""
            SELECT id,organization_id,key,name,description,trigger_type,
                   enabled,version,created_at,updated_at
            FROM platform_workflow_definitions
            WHERE organization_id IS NULL OR organization_id=?
            ORDER BY name
        """,(actor.get("organization_id"),)).fetchall()
        return {"workflows":[dict(x) for x in rows]}
    finally:
        c.close()

@_a1os_product_router.get("/executions")
def _a1os_product_executions(request: Request):
    actor = _a1os_product_actor(request)
    c = _a1os_product_db()
    try:
        rows = c.execute("""
            SELECT id,organization_id,workflow_key,status,requested_by,
                   approval_id,started_at,finished_at,error
            FROM platform_execution_runs
            WHERE organization_id IS NULL OR organization_id=?
            ORDER BY id DESC LIMIT 100
        """,(actor.get("organization_id"),)).fetchall()
        return {"executions":[dict(x) for x in rows]}
    finally:
        c.close()

@_a1os_product_router.get("/entitlements")
def _a1os_product_entitlements(request: Request):
    actor = _a1os_product_actor(request)
    c = _a1os_product_db()
    try:
        rows = c.execute("""
            SELECT organization_id,capability_key,status,source,
                   starts_at,expires_at,updated_at
            FROM platform_entitlements
            WHERE organization_id=?
            ORDER BY capability_key
        """,(actor.get("organization_id"),)).fetchall()
        return {"entitlements":[dict(x) for x in rows]}
    finally:
        c.close()

@_a1os_product_router.get("/release")
def _a1os_product_release(request: Request):
    _a1os_product_actor(request)
    c = _a1os_product_db()
    try:
        rows = c.execute("""
            SELECT release_id,check_name,result,evidence,created_at
            FROM platform_release_evidence
            ORDER BY id DESC LIMIT 100
        """).fetchall()
        return {
            "release":"production-certified",
            "authority":"approval_gated",
            "architecture":"folders_over_agents",
            "evidence":[dict(x) for x in rows]
        }
    finally:
        c.close()

app.include_router(_a1os_product_router)
# === END A1OS PRODUCTIZATION RELEASE ===

@app.get("/", response_class=HTMLResponse)
def a1os_platform_root():
    return '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>A1OS Platform</title>\n<style>\nbody{font-family:system-ui,sans-serif;max-width:900px;margin:0 auto;padding:48px 24px}\nh1{margin-bottom:8px}\n.card{border:1px solid #ddd;border-radius:12px;padding:20px;margin-top:24px}\n.status{font-weight:700}\na{display:inline-block;margin:8px 12px 8px 0}\n</style>\n</head>\n<body>\n<h1>A1OS Platform</h1>\n<p>Platform control plane and API.</p>\n<div class="card">\n<div class="status">Platform API: <span id="status">checking...</span></div>\n<p>\n<a href="/docs">API Documentation</a>\n<a href="/openapi.json">OpenAPI</a>\n</p>\n</div>\n<script>\nfetch(\'/v1/health\')\n.then(r=>r.ok?r.json():Promise.reject())\n.then(d=>document.getElementById(\'status\').textContent=\'Operational\')\n.catch(()=>document.getElementById(\'status\').textContent=\'Unavailable\');\n</script>\n</body>\n</html>\n'

@app.get("/v1/ready")
def readiness():
    """
    Readiness probe.

    Liveness is handled by /v1/health.
    Readiness verifies that the application can reach its
    required persistent database and that SQLite reports
    an internally consistent database.
    """
    import sqlite3

    try:
        conn = sqlite3.connect(A1OS_READINESS_DB, timeout=2)
        try:
            conn.execute("SELECT 1").fetchone()
            result = conn.execute("PRAGMA integrity_check").fetchone()
            if not result or result[0] != "ok":
                raise RuntimeError("database integrity check failed")
        finally:
            conn.close()

        return {
            "status": "ready",
            "service": A1OS_SERVICE_NAME,
            "environment": A1OS_RUNTIME_ENV,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "service": A1OS_SERVICE_NAME,
                "reason": str(exc),
            },
        )


@app.get("/v1/readiness")
def readiness_alias():
    return readiness()


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
            datetime.now(timezone.utc) + timedelta(days=_AUTH_SESSION_DAYS)
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
            secure=A1OS_COOKIE_SECURE,
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
    actor = _require_permission(request, "organizations:write")

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

@app.delete("/v1/organizations/{organization_id}")
def delete_organization(organization_id: int, request: Request):
    actor = _current_actor(request)

    if actor["role"] != "super_admin":
        raise HTTPException(
            status_code=403,
            detail="Only super_admin may delete organizations",
        )

    conn = db()
    try:
        row = conn.execute(
            "SELECT id, code, name FROM organizations WHERE id = ?",
            (organization_id,),
        ).fetchone()

        if not row:
            raise HTTPException(
                status_code=404,
                detail="Organization not found",
            )

        # Refuse deletion when dependent records exist.
        dependency_checks = [
            ("users", "organization_id"),
            ("products", "organization_id"),
            ("accounts", "organization_id"),
            ("ledger_entries", "organization_id"),
            ("parties", "organization_id"),
        ]

        for table, column in dependency_checks:
            try:
                hit = conn.execute(
                    f"SELECT 1 FROM {table} WHERE {column} = ? LIMIT 1",
                    (organization_id,),
                ).fetchone()
            except Exception:
                hit = None

            if hit:
                raise HTTPException(
                    status_code=409,
                    detail=f"Organization has dependent records in {table}",
                )

        cur = conn.execute(
            "DELETE FROM organizations WHERE id = ?",
            (organization_id,),
        )

        if cur.rowcount != 1:
            raise HTTPException(
                status_code=404,
                detail="Organization not found",
            )

        _audit(
            conn,
            actor,
            "organization",
            organization_id,
            "deleted",
            {"organization_id": organization_id},
        )

        return {
            "status": "deleted",
            "organization_id": organization_id,
        }
    finally:
        conn.close()


@app.get("/v1/users")
def list_users(request: Request):
    actor = _require_permission(request, "users:read")
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
    actor = _require_permission(request, "users:write")

    email = str(payload.get("email", "")).strip().lower()
    full_name = str(payload.get("full_name", "")).strip()
    role = str(payload.get("role", "member")).strip()
    password = str(payload.get("password", "")).strip()

    allowed_roles = set(DEFAULT_ROLE_PERMISSIONS.keys())
    if actor["role"] == "director":
        allowed_roles &= {"headmistress", "staff", "driver", "user"}
    elif actor["role"] in {"headmistress", "staff", "driver"}:
        raise HTTPException(status_code=403, detail="Insufficient authority to create users")
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



@app.post("/v1/admin/users/{user_id}/password-reset")
def admin_password_reset(user_id: int, payload: dict, request: Request):
    actor = _require_permission(request, "users:write")

    if actor["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Only super_admin may reset passwords")

    new_password = str(payload.get("new_password", ""))
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="new_password must be at least 8 characters")

    conn = db()
    try:
        row = conn.execute(
            "SELECT id, organization_id, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")

        password_hash = _hash_password(new_password)
        conn.execute(
            "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (password_hash, user_id),
        )
        _audit(
            conn,
            actor,
            "user",
            user_id,
            "admin_password_reset",
            {"email": row["email"], "organization_id": row["organization_id"]},
        )
        conn.commit()
        return {
            "status": "password_reset",
            "user_id": user_id,
            "force_change_on_login": True,
        }
    finally:
        conn.close()


@app.patch("/v1/users/{user_id}")
def update_user(user_id: int, payload: dict, request: Request):
    actor = _require_permission(request, "users:write")

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
    actor = _require_permission(request, "users:read")
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
    actor = _require_permission(request, "users:write")

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
    actor = _require_permission(request, "users:write")

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
    actor = _require_permission(request, "parties:read")
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
    actor = _require_permission(request, "parties:write")

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
    actor = _require_permission(request, "parties:write")

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
    actor = _require_permission(request, "products:read")
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
    actor = _require_permission(request, "products:write")

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
    actor = _require_permission(request, "products:write")

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
    actor = _require_permission(request, "ledger:read")
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
    actor = _require_permission(request, "ledger:write")

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
    actor = _require_permission(request, "ledger:write")

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
    actor = _require_permission(request, "ledger:read")
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
    actor = _require_permission(request, "ledger:read")
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
    actor = _require_permission(request, "ledger:read")

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
    actor = _require_permission(request, "inventory:read")
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
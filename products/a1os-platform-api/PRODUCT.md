# A1OS Platform API

Multi-tenant platform backend serving industry-specific frontend applications.

- **Port**: 3013
- **Backend**: FastAPI + SQLite (`deployments/a1os-platform/data/a1os-platform.db`)
- **Auth**: SSO-style opaque session tokens (PBKDF2-HMAC-SHA256 password hashing), role-based permissions
- **DB bootstrap**: tables created from `database/schema.sql`; first-run seeds the `ICR` (Image Coffee Roastery) organization and a `super_admin` user
- **Admin seed** (override via env): `A1OS_PLATFORM_ADMIN_EMAIL` (default `admin@a1os.io`), `A1OS_PLATFORM_ADMIN_PASSWORD` (default `A1os.Admin@2026`)

## Run

```
cd products/a1os-platform-api && python3 -m uvicorn api.app:app --host 127.0.0.1 --port 3013
```

or `./run-production.sh`.

## Modules (v1.0)

| Area | Endpoints |
| --- | --- |
| Health | `/v1/health`, `/health` |
| Auth | `/auth/login`, `/auth/me`, `/auth/logout`, `/auth/change-password` |
| Organizations | `GET/POST /organizations`, `PATCH /organizations/{id}` |
| Users | `GET/POST /users`, `PATCH /users/{id}` |
| Roles | `GET/POST /roles`, `PATCH /roles/{id}` |
| Parties | `GET/POST /parties`, `PATCH /parties/{id}` (customer/supplier/farmer/buyer) |
| Products | `GET/POST /products`, `PATCH /products/{id}` |
| Accounts | `GET/POST /accounts` |
| Ledger | `POST /ledger`, `GET /ledger`, `GET /ledger/balances`, `GET /ledger/trial-balance` |
| Inventory | `GET /inventory/items`, `POST /inventory/movements`, `GET /inventory/movements` |
| Notifications | `GET/POST /notifications` |
| Audit | `GET /audit` |
| Realtime | `WS /ws?token=...` (per-organization broadcast) |

## Principles

- UI-only frontends: all data flows through these APIs; no business logic in clients.
- Multi-tenant via `organization_id`; every resource is org-scoped.
- One backend, many industry frontends (coffee ERP, school OS, charity, business, music label).

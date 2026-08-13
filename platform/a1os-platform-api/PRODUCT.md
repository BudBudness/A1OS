# A1OS Platform API

Multi-tenant platform backend serving industry-specific frontend applications.

- **Port**: 3013
- **Backend**: FastAPI + SQLite (`deployments/a1os-platform/data/a1os-platform.db`)
- **Auth**: SSO-style opaque session tokens (PBKDF2-HMAC-SHA256 password hashing), role-based permissions
- **Admin seed**: administrator identity is provisioned through the protected platform secret authority; production credentials are not stored in source documentation or application environment files.

## Run

```
cd products/a1os-platform-api && python3 -m uvicorn api.app:app --host 127.0.0.1 --port 3013
```

or `./run-production.sh` (loads `.env.production` if present).

## Production deployment (v1.0.0)

Live on the a1os-prod Cloudflare tunnel (`pyongcity.org` zone):

| Public hostname | Service |
| --- | --- |

- Both CNAMEs route through tunnel `a1os-prod` (`7fdd3dce`); the platform API stays bound to `127.0.0.1` — only the tunnel exposes it.
- Watchdog (`ops/a1os-production-watchdog.sh`) health-checks `http://127.0.0.1:3013/v1/health` and `http://127.0.0.1:3000/login` hourly and restarts either service if down.

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

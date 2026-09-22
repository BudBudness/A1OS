# A1OS Platform API

Multi-tenant platform backend serving industry-specific frontend applications.

- **Port**: 3013
- **Backend**: FastAPI + SQLite (`runtime/a1os-platform-api/deployments/a1os-platform/data/a1os-platform.db`)
- **Auth**: SSO-style opaque session tokens (PBKDF2-HMAC-SHA256 password hashing), role-based permissions
- **Admin seed**: administrator identity is provisioned through the protected platform secret authority; production credentials are not stored in source documentation or application environment files.

## Run

```
cd .private/platform/a1os-platform-api/api && \
  PYTHONPATH="$PWD:$PWD/../../../:$PWD/../../.." \
  python3 -m uvicorn app:app --host 127.0.0.1 --port 3013 \
  --workers 1 --proxy-headers
```

or `runtime/a1os-platform-api/run-production.sh`.

## Production deployment

The canonical application binds to `127.0.0.1:3013`. Public ingress is environment-managed through the `a1os-prod` Cloudflare tunnel; tunnel/DNS configuration is not stored in this repository.

| Public hostname | Service |
| --- | --- |
| `a1os.ug` / `www.a1os.ug` | A1OS public website on 3013 |
| `app.a1os.ug` | A1OS Control Plane on 3013 |
| `api.a1os.ug` | A1OS Platform API on 3013 |

The same canonical runtime serves the A1OS web experiences and API. No second backend, database, or web-server process is required. Public domain activation remains an environment/DNS concern and must not be represented as complete until externally verified.

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

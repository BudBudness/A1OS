# A1OS

A1OS is a multi-tenant platform API and product frontend system. It provides
shared identity, tenancy, authorization, operational data, and governance
contracts so industry frontends can use one platform backend instead of
creating separate backends.

The shipped repository is centered on the **A1OS Platform API**, a FastAPI
application backed by SQLite. The verified canonical service is local and
listens on `127.0.0.1:3013`.

## Architecture

A1OS follows a **folders over agents** principle: the repository's explicit
platform, product, runtime, gate, and archive boundaries are the source of
truth for execution and ownership. AI assistance may propose work, but it is
not an execution authority.

```text
Industry frontend verticals
            |
            v
A1OS Platform API (:3013)
            |
            +-- identity, tenancy, RBAC, authorization
            +-- organizations, users, roles, parties
            +-- products, inventory, ledger, POS
            +-- education, notifications, audit, WebSocket updates
            +-- approvals, workflows, deployments, health, billing projections
            |
            v
SQLite platform state
```

Verticals own UI pages, components, state, styles, assets, and frontend tests.
The shared platform owns authentication, tenancy, authorization, persistence,
and infrastructure contracts. A vertical must not introduce a separate
backend, database, watchdog, or infrastructure stack.

## Canonical runtime

The authoritative application entrypoint is:

```text
.private/platform/a1os-platform-api/api/app.py
```

The canonical API base URL is:

```text
http://127.0.0.1:3013/v1
```

The desired service state is declared in `ops/services.json`. The reconciler
probes the local health URL and uses the registered adapter only when recovery
is required. The active service is the platform API on port 3013; do not
start a second owner for that port.

For local development, use the Termux Python environment and run the
application from its API directory:

```bash
cd .private/platform/a1os-platform-api/api
PYTHONPATH="$PWD" python3 -m uvicorn app:app \
  --host 127.0.0.1 --port 3013 --workers 1
```

The deployed runtime uses the same `app:app` entrypoint under its service
manager. Keep one worker because authentication rate limiting is in-process.

## Health and readiness

Liveness and readiness are separate checks:

```bash
curl -fsS http://127.0.0.1:3013/v1/health
curl -fsS http://127.0.0.1:3013/v1/ready
```

`/v1/health` reports API liveness. `/v1/ready` verifies that the configured
SQLite database is reachable and passes `PRAGMA integrity_check`.
`/v1/readiness` is an alias for readiness.

`./a1ctl status` queries the canonical 3013 health endpoint. The API also
publishes interactive documentation at `/docs` and its OpenAPI document at
`/openapi.json`.

## Implemented platform capabilities

The current API includes:

- Authentication sessions with bearer-token or HTTP-only cookie transport
- PBKDF2-HMAC-SHA256 password hashing, logout, password change, and session
  invalidation after a password change
- Organization-scoped users, roles, permissions, parties, and products
- Inventory items and stock movements
- Accounts, double-entry ledger entries, balances, and trial balance
- Point-of-sale sales and sale detail endpoints
- School operations: students, parents, admissions, attendance, fees,
  transport, site content, and notifications
- Audit records and organization-scoped WebSocket broadcasts
- Platform projections for resources, capabilities, products, workflows,
  approvals, billing, deployments, health, terminal metadata, and release
  evidence

The API is the source of truth for domain data. Frontends consume these
contracts rather than owning an independent business database.

## Command Center

The owner-facing Command Center is served at:

```text
http://127.0.0.1:3013/command-center
```

Its static contract is
`.private/platform/a1os-platform-contract/runtime/command-center.html`.
The UI reads authenticated projections under `/v1/command-center/`,
including dashboard, organizations, resources, approvals, health,
deployments, billing, automation, terminal, and security views.

Command Center terminal access is explicitly restricted. The platform
reports `arbitrary_shell: false`; terminal metadata is available only to
authorized platform roles, and the control surface remains approval-gated.

## Authentication and authority

Login is:

```text
POST /v1/auth/login
```

Authenticated requests use either:

```text
Authorization: Bearer SESSION_TOKEN
```

or the `a1os_session` HTTP-only cookie. Protected routes enforce the actor's
organization and permissions. The implementation includes role defaults for
platform administrators, owners, managers, directors, headmistresses, staff,
drivers, and users, with organization-level permission overrides.

Authentication attempts are rate-limited in memory. Password changes require
the current password and a new password of at least eight characters, then
invalidate the user's other sessions. Credentials, tokens, and environment
secrets are intentionally not documented here.

The execution model is human-authority-first: AI is not an execution
authority, terminal access is not arbitrary shell access, and approval,
authorization, audit, and verification remain platform responsibilities.

## Repository structure

| Path | Purpose |
| --- | --- |
| `.private/platform/a1os-platform-api/api/` | Canonical FastAPI application, boundary helpers, and platform SQLite state |
| `.private/platform/a1os-platform-contract/runtime/` | Command Center contract and runtime UI |
| `ops/` | Desired service registry, reconciler, adapters, watchdog, and backup operations |
| `runtime/scripts/` | Managed product deployment scripts |
| `clients/little-oaks/` | Little Oaks frontend source and its build configuration |
| `products/verticals/` | Frontend-only industry vertical contracts and product metadata |
| `A1OS_ENGINEERING_GATES/` | Contract, authorization, integrity, recovery, and security gates |
| `archive/legacy-3011-runtime/` | Retired legacy runtime scripts and inventory preserved as history |
| `a1ctl` | Small control CLI targeting the canonical 3013 API |

The `infra/` and `deployment/` directories are scaffolding, not the active
local production target. The active platform service is the Termux-managed
API described above.

## Products and verticals

`products/verticals/VERTICALS.json` catalogs frontend-contract verticals for
school, salon/barber, real estate, logistics, music/artist, events,
agriculture, and construction. Catalog status is
`implementation-ready`; these entries describe frontend contracts, not
separate backend deployments.

Little Oaks is present as a managed frontend product under
`clients/little-oaks/`. Its deployment metadata identifies the A1OS Platform
API as its backend and A1OS Core as its authentication, tenancy,
authorization, and RBAC authority. The managed deployment script builds that
source and publishes the production artifact under
`products/verticals/little-oaks/`, then verifies the managed local frontend
service and its assets.

The school vertical is present under `products/verticals/school/` with
frontend pages and contract metadata for organizations, users, roles,
students, parents, admissions, attendance, fees, notifications, audit, and
site content.

## Engineering gates and evidence

The gate suite is under `A1OS_ENGINEERING_GATES/`. It covers API contract
regression, RBAC, session-token security, security boundaries, CRUD
atomicity, foreign-key integrity, rollback, audit integrity, tenant
isolation, restart recovery, backup/restore, the canonical data model, and
the API contract freeze.

Run the complete sequence with the repository's documented Termux environment
and an administrator password supplied through the existing protected
environment mechanism:

```bash
./A1OS_ENGINEERING_GATES/RUN_ALL_WORK_UNITS.sh
```

Gate outputs and generated OpenAPI evidence belong under
`A1OS_ENGINEERING_GATES/evidence/` and are ignored by repository policy.
Do not place passwords, tokens, private keys, or database credentials in the
repository.

## Deployment and public ingress

The repository verifies the canonical API locally on port 3013. `ops/services.json`
also defines a Cloudflare edge observer as an external, observer-only service;
an external edge failure must not cause the local API to be restarted when
the local health probe is passing. Public ingress is environment-managed and
is separate from the canonical localhost API contract. No public credential
or tunnel secret is part of this documentation.

## Active versus historical material

Active runtime and source are the paths used by the 3013 service, its
reconciler, platform contract, gates, clients, and frontend verticals.

The `archive/legacy-3011-runtime/` directory contains exact copies of retired
3011-era scripts and an inventory retained for historical reference. The
timestamped files under
`.private/platform/a1os-platform-contract/releases/` are historical release
snapshots, not runtime entrypoints. They are intentionally preserved without
normalizing their original contents.

## Current status

The canonical repository state is the `build/a1os-next-stack` branch. The
platform's verified operational checks are:

```text
GET http://127.0.0.1:3013/v1/health  -> status=ok
GET http://127.0.0.1:3013/v1/ready   -> status=ready
```

These checks confirm the active local API and its persistent database
readiness; they do not claim that every cataloged frontend vertical is a
deployed production service.

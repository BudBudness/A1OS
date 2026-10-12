# Stramos Wisdom Charity — Standalone Migration Audit

**Purpose:** consolidate Stramos Wisdom Charity under A1OS without losing source, data, or deployment capability.

**Status:** initial source snapshot, tenant-scoped schema, and authenticated create/list API are implemented on the migration branch. Full workflow coverage, production verification, data cutover, and deployment checks are NOT complete. Do not delete the standalone repository yet.

## Repositories

- A1OS: https://github.com/BudBudness/A1OS
- Standalone source: https://github.com/BudBudness/StramosWisdomCharityOrg
- Standalone default branch: `main`
- Standalone source commit snapshotted into A1OS: `cf9eb3270c3dd1b77da8f90647d5ca5f8a78439c` (21 tracked files).
- Snapshot commit in A1OS migration branch: `5f128a75c540355bd3b02d776a235b5783489654`.

## Current A1OS footprint

A1OS currently has only a product descriptor at:
`products/verticals/charity/deployments/stramoswisdomcharityorg/PRODUCT.md`

That descriptor lists beneficiaries, donors, projects, aid, donations, case management, and reporting. It does not prove those workflows are implemented.

The factory check in `tools/a1os_factory/final_definition_of_done.py` accepts the charity product descriptor as evidence. Its charity check is a presence check, not a runtime integration test. Update acceptance checks so a descriptor alone cannot certify the product.

Architecture documented in `products/PRODUCTIZATION.md`: A1OS owns shared identity, authorization, tenancy, audit, persistence and platform services; verticals own product workflows and UI. The migration must follow this boundary instead of blindly copying a second standalone backend into production.

## Standalone source inventory reviewed

Backend files:
- `backend/app/main.py` — SHA `718bef2473dfad175ae7222aa786246d666b7143`
- `backend/app/routes.py` — SHA `2ee71434514a907ad0f255b66b7151e8f6e3a970`
- `backend/app/models.py` — SHA `26b2d5edc1839496f59e570bda5bd55bccc56a93`
- `backend/app/schemas.py` — SHA `14a0ae9bbf7ec36c8a1278698aeea4a80b6d34db`
- `backend/app/database.py` — SHA `19ba88f8bd0bfe848c6b20b12ffd44b6e77bc069`
- `backend/app/settings.py` — SHA `00de1c25959416b2e10b21838aa05c9969200974`
- `backend/app/serializers.py` — SHA `c9c51e0318791d2b2aad9e81f4820bb0001ccfbc`
- `backend/app/data.py` — SHA `9eed8863e4d11bb998f579fd6ae19254213f0bd1`
- `backend/requirements.txt` — SHA `58ffc6fac990c6b0f1349c3cb3f7b1be80fb92b`

Other files:
- `frontend/package.json` — SHA `c68c0e6f31a4370b4ac9c7f344a89a65593cc992`
- `docker-compose.yml` — SHA `2a763f186594267f51986eea1f4218db09bd66f1`
- `README.md` — SHA `e1ab4d03548e17ef067692ca802a7d92f56a8731`
- CI: `.github/workflows/ci.yml` — SHA `8e4359d5511c6cac36bd6f90cd087b97318aaa09`

Source links:
- [Backend routes](https://github.com/BudBudness/StramosWisdomCharityOrg/blob/main/backend/app/routes.py)
- [Data models](https://github.com/BudBudness/StramosWisdomCharityOrg/blob/main/backend/app/models.py)
- [Schemas](https://github.com/BudBudness/StramosWisdomCharityOrg/blob/main/backend/app/schemas.py)
- [Database configuration](https://github.com/BudBudness/StramosWisdomCharityOrg/blob/main/backend/app/database.py)
- [Frontend](https://github.com/BudBudness/StramosWisdomCharityOrg/tree/main/frontend)
- [Docker Compose](https://github.com/BudBudness/StramosWisdomCharityOrg/blob/main/docker-compose.yml)
- [CI workflow](https://github.com/BudBudness/StramosWisdomCharityOrg/blob/main/.github/workflows/ci.yml)

## Capability mapping

| Standalone capability | Current implementation evidence | A1OS migration target |
|---|---|---|
| Public contact/program/event content | Routes backed partly by static data | Charity vertical content/workflows |
| Volunteer intake and records | POST/GET API + SQLAlchemy model | Charity workflow using A1OS identity/audit and approved persistence |
| Partner intake and records | POST/GET API + SQLAlchemy model | Charity partnership workflow |
| Donation intent | POST/GET API + SQLAlchemy model | Donation-intent workflow; keep distinct from confirmed payments |
| Outreach reporting | POST/GET API + SQLAlchemy model | Charity reporting workflow with permission-controlled media and records |
| Beneficiary management | A1OS descriptor only; no dedicated standalone model found in inspected files | Implement explicitly with restricted access and audit |
| Donor management | A1OS descriptor only; no dedicated donor model/workflow verified | Implement explicitly; do not equate donors with donation intents |
| Aid and case management | A1OS descriptor only; not verified in standalone implementation | Define workflows, roles, approvals, audit trail and tests |

## Migration implementation added on branch

- Source snapshot: `products/verticals/charity/migration-source/StramosWisdomCharityOrg/`.
- Additive schema: `migrations/001_charity_schema.sql`, loaded by platform API startup when present.
- API: authenticated `GET` and `POST /v1/charity/{resource}` for `programs`, `beneficiaries`, `cases`, `aid-allocations`, `donors`, `donation-intents`, `volunteers`, `partnerships`, and `outreach-reports`.
- Tenant ID comes from the authenticated actor; cross-tenant foreign references are rejected; create operations are audited.
- Donation intent status is server-defaulted to `intent`; clients cannot submit payment confirmation fields.
- Tests: `tests/test_charity_schema_migration.py` and `tests/test_charity_api.py`; both are included in CI. The initial schema-only CI run passed. The API integration suite is being verified after adding its FastAPI test dependencies.

These are initial intake/list capabilities, not a finished charity application. Update/approval/disbursement flows, payment provider reconciliation, frontend integration, and production cutover remain outstanding.

## Blocking risks before deletion

1. **Authorization:** inspected standalone list endpoints for volunteers, partners, donations and outreach reports show no route-level authentication/authorization dependency. Verify the deployment and implement server-side authorization before production.
2. **Tenant isolation:** no A1OS tenant context is evident in the inspected standalone models/routes. Add tenant-scoped access through the platform contract; test cross-tenant denial.
3. **Donation correctness:** donation intent is not proof of money received. Payment provider verification, idempotency, reconciliation, refund handling and ledger posting are not established by inspected files.
4. **Database migration:** SQLAlchemy `create_all()` is used at startup; add versioned migrations and a tested backup/restore path.
5. **Secrets/config:** Docker Compose contains a fixed development database password. Keep production credentials out of source and use deployment-managed secrets.
6. **Frontend and assets:** review and migrate the complete frontend source and static assets; frontend package/build alone is not sufficient evidence.
7. **Production dependencies:** identify the live domain, deployment project, environment variables, database and data ownership. Do not remove or redirect them until cutover is verified.
8. **Source backup:** before repository deletion, create a durable archive of the complete standalone Git history and source, verify it can be retrieved, and record the final commit SHA. No archive was created by this audit.

## Required acceptance evidence

- [x] Full source snapshot and exact source commit SHA recorded.
- [ ] All relevant frontend/backend behavior mapped to A1OS-owned modules.
- [ ] No duplicate independent auth, tenancy, or audit implementation remains.
- [ ] Authorization and cross-tenant isolation tests pass.
- [ ] Database migrations and backup/restore tested.
- [ ] Volunteer, partner, donation-intent, outreach-report and public-content flows pass integration/E2E tests.
- [ ] Beneficiary, donor, aid and case-management requirements are implemented or explicitly excluded by signed scope.
- [ ] Payment statuses are provider-verified; intent cannot be mistaken for settled money.
- [ ] CI/build/security checks pass on the proposed release commit.
- [ ] Deployment, environment variables, domains, monitoring and rollback verified.
- [ ] Data has been migrated/reconciled if applicable, with no loss.
- [ ] Standalone repo archived or deleted only after the above are signed off.

## Decision

Proceed with migration work on this branch. Keep `BudBudness/StramosWisdomCharityOrg` intact until implementation, source backup, data/deployment cutover, and acceptance evidence are complete. This audit document is not itself proof of a successful migration.

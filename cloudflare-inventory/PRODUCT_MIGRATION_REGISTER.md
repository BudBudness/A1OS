# Product Migration Register — GitHub + Cloudflare + Termux

**Owner:** Eddie Billions  
**Control-plane repository:** `BudBudness/A1OS`  
**Register version:** 1.0  
**Last reviewed:** 2026-11-06  
**Status:** Discovery baseline; migrations not yet executed

## 1. Binding platform decision

All products in this register are to converge on the following approved platform boundary:

- **GitHub:** source of truth, issues, pull requests, CI/CD, release artifacts, change history and audit trail.
- **Cloudflare:** application runtime and edge delivery, database, object storage, DNS, access/security and observability.
- **Termux:** local engineering workstation, repository orchestration, diagnostics, migration tooling and independent verification.

Vercel, Supabase, Convex, Macaly-hosted runtime, and any other unapproved hosting, database, identity, CI/CD or infrastructure provider are migration-out targets. They are not approved as permanent runtime dependencies.

This register does not authorize deletion, production cutover, paid resource expansion, credential rotation, DNS changes or data destruction. Existing services remain in place until their replacement passes the release gates.

## 2. Cloudflare target service patterns

Use the smallest Cloudflare service set that satisfies each product's measured workload:

| Concern | Default target | Constraints |
|---|---|---|
| Web/API runtime | Cloudflare Workers | Prefer Workers-native application/API; use Pages only when static/frontend delivery materially benefits. |
| Relational data | Cloudflare D1 | Schema, indexes, constraints, migration and transaction limits must be validated against workload. |
| Files and media | Cloudflare R2 | Private by default; explicit upload/download authorization and lifecycle rules. |
| Staff/admin identity boundary | Cloudflare Access | Use for staff/admin surfaces where suitable; do not assume Access alone solves consumer identity. |
| Consumer authentication | Worker-owned authentication design using supported Cloudflare primitives | Specify threat model, sessions, password/OAuth requirements, recovery, abuse controls and audit before implementation. No external identity provider by default. |
| DNS and edge security | Cloudflare DNS, WAF and applicable security controls | DNS cutover is a separately gated release action. |
| CI/CD | GitHub Actions + Wrangler | Protected environments, least-privilege staging and production identities, immutable commit provenance. |
| Observability | Cloudflare logs/metrics plus GitHub release evidence | No secrets or sensitive personal data in logs. |
| Large datasets / analytical artifacts | R2 for immutable objects; D1 for metadata and bounded operational records | Benchmark before selecting D1 for high-volume time-series or analytical queries. |

Do not add KV, Queues, Durable Objects, Workflows, Containers, Stream or other Cloudflare products by default. Add only where a documented workload requirement, plan/limits review, cost control and isolation design justify them. Do not introduce VMs, VPSs or physical servers as migration shortcuts.

## 3. Product migration register

| Product / repository | Observed current architecture and dependency | Cloudflare target direction | Status / key work |
|---|---|---|---|
| A1OS — `BudBudness/A1OS` | Root app has Vercel deployment/cron and Supabase-backed task queue, storage and worker paths. Product verticals include Legal, Little Oaks and charity. | Keep A1OS as the engineering/control-plane host. Move runtime and task execution to Workers; D1 for task/workflow metadata; R2 for artifacts and files. Use GitHub Actions for release orchestration. | **Discovery required.** Separate control-plane workspace from legacy root runtime. Map all task workers, cron, RPCs, secrets, data and vertical dependencies. |
| Little Oaks — currently represented in A1OS and Vercel/Supabase projects | Vercel frontend and Supabase database/auth integration. | Workers frontend/API; D1 for nursery operations; R2 for documents/media; Cloudflare Access for staff/admin access where suitable. | **Discovery required.** Confirm canonical code location, live data, users, roles, fee records, backups and custom-domain ownership before migration. |
| GUZA GURA — `BudBudness/GUZA_GURA-` | Next.js PWA; README and package confirm Vercel + Supabase; Supabase browser/server SDKs and environment configuration. | Workers-compatible Next.js deployment or Workers API + frontend; D1 listings, sellers, enquiries and moderation; R2 listing images; explicit consumer/staff auth design. | **Discovery required.** Implement schema, auth, image upload, listing lifecycle, seller controls and moderation before cutover. |
| Ether Tours & Travel — `BudBudness/Ether_Tours-Travel` | Next.js; README confirms Vercel + Supabase PostgreSQL/Auth/RLS; initial catalogue/enquiry migration. | Workers frontend/API; D1 catalogue and enquiries; R2 media/documents; Access for staff/admin. | **Discovery required.** Port and test RLS-equivalent authorization, enquiry validation, spam controls, staff workflows and content integrity. |
| Dexta Buyer Signal — `BudBudness/Dexta_Buyer_Signal` | README confirms Macaly UI/workspace and TanStack Start; Convex backend/data/functions and Convex Auth. Vercel project also exists. | Workers API/application; D1 for structured prospects, evidence metadata and lifecycle; R2 for source snapshots/reports; redesign authentication without Convex Auth. | **Discovery required.** Export/inspect Convex schema, functions, indexes, auth flows, scheduled jobs, file storage, data volume and OAuth needs. Preserve provenance and consent boundaries. |
| SMC Agent — `BudBudness/SMC-Agent-` | Next.js/Vercel; application API uses Supabase REST for runs, reports, hypotheses and evidence. | Workers API/UI; D1 for bounded metadata and research records; R2 for historical market datasets, derived artifacts and reports. | **Discovery required.** Benchmark query patterns and dataset volume. Do not force high-volume OHLC/time-series into D1 without performance evidence. Validate historical data lineage and reproducibility. |
| Stramos Wisdom Charity — `BudBudness/StramosWisdomCharityOrg` | README describes Next.js, FastAPI, PostgreSQL, Docker Compose and GitHub Actions. No Vercel/Supabase dependency detected in the limited inspected README/search pass. | Workers frontend/API after compatibility assessment; D1 for beneficiary/program/case metadata; R2 for protected documents and evidence. | **Discovery required.** Inspect full backend, schema, attachments, authorization, tenant boundaries, audit requirements and data residency/retention. No assumption that FastAPI/Docker can be deployed unchanged to Workers. |
| PyongLive — `BudBudness/PyongLive` | Already Cloudflare-first: Workers, D1, R2, Cloudflare Stream; GitHub Actions. | Retain Cloudflare architecture; improve production readiness, broadcast/replay verification, security, observability and cost controls. | **Cloudflare-aligned.** Treat current Worker/D1/R2 as production resources; never reuse for staging tests. Stream remains a product-specific paid service and must be cost-governed. |

## 4. Migration lifecycle and gates

Every product follows the same sequence. Status cannot advance without evidence.

1. **DISCOVER** — inventory repositories/branches, deployments, runtime bindings, external integrations, domains, secrets by name (never values), data stores, schemas, files, scheduled jobs, users and permissions.
2. **SPECIFY** — produce product constitution, target architecture, data classification, service mapping, migration/rollback plan, cost estimate and acceptance criteria.
3. **ARCHITECT** — design Workers runtime, D1 schema, R2 layout, identity, authorization, observability, abuse controls, backup and recovery.
4. **PLAN** — create ordered migration issues, ownership, dependencies, risk tier, staging resources and release gates.
5. **BUILD** — implement Cloudflare-compatible code and versioned D1 migrations; create synthetic fixtures only in staging.
6. **VERIFY** — build/typecheck/lint/test; security and authorization tests; schema parity; data reconciliation; file counts/checksums; performance; backup/restore; end-to-end workflows.
7. **RELEASE** — approve production resources and credentials; deploy; smoke test; only then schedule separately approved DNS/traffic cutover.
8. **OPERATE** — monitor errors, latency, usage, security events, backup health and cost; maintain rollback readiness.
9. **DECOMMISSION** — export required records, verify retention obligations, confirm replacement stability, remove old traffic and integrations, then delete legacy projects only after explicit final confirmation and verified recovery/retention.

### Mandatory per-product release gates

- Source and destination ownership established.
- Complete data inventory and classification.
- Verified source backup/export and tested restoration path.
- D1 schema and migration reviewed; data counts and critical records reconciled.
- R2 object inventory, checksums and access controls verified.
- Authentication, authorization, tenant isolation and staff/admin boundaries tested.
- Secrets moved through approved protected environments; no secret values in Git or logs.
- Workflows, cron/scheduled jobs, webhooks, notifications and external integrations accounted for.
- Domain and DNS ownership confirmed; rollback plan tested.
- Cost/usage budget and alerts approved.
- Production health, synthetic transaction and end-to-end acceptance checks pass.
- Product owner accepts cutover evidence.
- Legacy provider deletion remains a separate, explicit decommission approval.

## 5. Global constraints

- No bulk rewrite or deletion based only on provider-name matches.
- No production data copied into staging; synthetic data only.
- No production credentials or bindings reused in staging.
- No user-facing traffic cutover before parity and rollback checks pass.
- No provider project, database, bucket, domain, integration or secret is deleted until dependencies and retention obligations are verified.
- No claim of migration completion without repository commit, successful CI, Cloudflare deployment evidence and independent runtime/data verification.
- Preserve product-specific behavior; standardize operations, not product requirements.
- The canonical control-plane code must remain isolated from product runtime code and must pass the provider-boundary policy.

## 6. Current blockers

1. Full repository/branch and workflow inventory is not yet complete for all projects.
2. Live Vercel/Supabase/Convex data volumes, storage objects, auth users, schemas and integrations have not been fully inspected.
3. Cloudflare account plan, product entitlements, quotas and per-product cost envelopes need verification.
4. A dedicated least-privilege Cloudflare deployment identity for staging and production is not yet verified.
5. Staging owner, independent approver, numeric budget caps and approved staging hostname/access boundary are unresolved.
6. Product-specific data retention, privacy, recovery and cutover owners must be identified.
7. Existing Vercel deployment checks are failing because the Vercel account reports deployment blocked; this is not evidence that Cloudflare replacements are ready.

## 7. Immediate next actions

- Complete a repository-by-repository code, workflow and dependency inventory.
- For each external provider, inventory resources and dependencies without reading secret values or mutating services.
- Build per-product target architecture and data mapping documents.
- Prioritize A1OS control-plane isolation and PyongLive operational hardening; then sequence product migrations by business criticality and dependency complexity.
- Keep legacy infrastructure online until each replacement is independently verified.
- Update this register with commit links, issue IDs, evidence and status changes as work completes.

**Current overall status:** `DISCOVERY_BASELINE`  
**Production migrations completed:** `0`  
**Legacy provider resources deleted:** `0`  
**Production infrastructure modified by this register:** `false`


## 8. Additional repository evidence — A1OS local runtime and product constraints

The A1OS repository's `AGENTS.md` and `ops/services.json` establish that A1OS is not simply a Vercel-hosted application:

- The documented operator environment is Termux on Android, with local Python services and a local SQLite database.
- The documented Cloudflare Tunnel `a1os-prod` exposes `little-oaks.pyongcity.org` and routes API traffic to a local service; the remaining hostname traffic is routed to a local web service.
- The tracked service registry lists `a1os-core` on local port 3011, `platform-api` on local port 3013, and an external Cloudflare edge observer.
- The operator documentation describes scheduled reconciliation, health checks, database backups, notifications and backup transfer to a private GitHub repository.
- The Vercel configuration separately defines a one-minute cron for `/v1/worker/run`; the production E2E workflow is still coupled to the Vercel URL and Supabase task persistence.

**Architecture correction:** preserve Termux as an approved execution environment. Do not automatically rewrite every A1OS local service into a Worker. First classify each component as (a) local Termux operator/runtime service, (b) Cloudflare-hosted public edge/API service, or (c) GitHub-managed CI/release task. Replace Vercel cron and Supabase task persistence with an explicitly designed Cloudflare/GitHub workflow only after semantics, reliability and recovery are verified.

**Unresolved topology discrepancy:** the operator guide describes an API route to local port 3012, while the tracked `ops/services.json` registers `platform-api` on port 3013. Reconcile the live Termux configuration, tunnel ingress, launchers and health checks before changing routes or deployment targets. The GitHub repository alone cannot verify the active local process or tunnel configuration.

Additional product constraints found in repository manifests:

- **GUZA GURA:** Next.js 15 / React 19 with Supabase SSR and JS SDKs; its CI currently runs typecheck, lint and build only. Its environment template includes a server-only service-role variable. Replace the integration with explicit Worker API contracts and never expose privileged keys to browser code.
- **Ether Tours:** Next.js 15 / React 19 with Supabase SSR and JS SDKs; CI is typecheck/lint/build. The current environment template uses Supabase URL and publishable/anon key. Rebuild the data-access and authorization layer rather than mechanically replacing SDK imports.
- **Dexta:** the committed webapp directly depends on Convex and Convex Auth; its CI tests, audits production dependencies and builds the Vite/TanStack application. The README's Macaly workspace is not evidence that all UI source is present in GitHub. Confirm source completeness and exportability before retiring Macaly.
- **SMC Agent:** combines Next.js with a Python research/dashboard stack whose dependencies include pandas, NumPy and Streamlit; its Vercel configuration currently packages a Python API function. Treat the research compute and data plane as a separate compatibility/performance workstream; do not assume a direct Workers port or put large historical time-series into D1 without benchmarks.
- **Stramos Charity:** its checked-in Compose file defines PostgreSQL, FastAPI and Next.js services. A local-development database password is embedded in the Compose configuration; rotate/remove any reuse, move development credentials to local ignored environment files, and ensure production credentials are generated separately. This is a configuration hygiene finding, not evidence that a production credential was exposed.
- **PyongLive:** its Wrangler config binds the production Worker to `pyonglive-db` and `pyonglive-assets`; GitHub deployment workflow applies remote D1 migrations before deploying code and then runs production endpoint checks. Keep that production pipeline and resource binding isolated from any staging experiment.

**Next A1OS verification:** inspect the live Termux checkout and Cloudflare Tunnel ingress read-only; compare them with `AGENTS.md`, `ops/services.json`, Vercel cron configuration and the GitHub workflows. Capture exact service/port ownership, current database state and backup/restore evidence before drafting the A1OS runtime migration.

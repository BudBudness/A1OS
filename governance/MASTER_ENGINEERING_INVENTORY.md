# Eddie Billions Master Engineering Inventory

**Status:** Initial discovery snapshot — incomplete, not an access attestation.  
**Owner:** Eddie Billions  
**Policy:** EB-CAEIO-001  
**Last discovery:** 2026-11-05

## Coverage status
- GitHub connected identity: 7 repositories returned; second page empty.
- All 7 returned repositories report owner affiliation and admin-level repository permissions in connector metadata.
- GitHub organization/account completeness: not independently verified beyond connected identity visibility.
- Cloudflare account inventory: BLOCKED; no Cloudflare account-management tools or Cloudflare plugin are exposed in this ChatGPT execution session.
- GitHub Actions and deployment permissions: not yet independently tested across all repositories.
- Private repository completeness: UNVERIFIED.

## GitHub repositories discovered
| Repository | Default branch | Visibility | Product / architecture evidence |
|---|---|---|---|
| BudBudness/A1OS | main | public | Autonomous multi-engine orchestration platform; Python core, Node tooling, product verticals; Cloudflare tunnel and Termux-hosted services documented. Candidate control-plane host only; not yet approved as canonical host. |
| BudBudness/PyongLive | main | public | Cloudflare Workers, D1, R2, Stream; GitHub Actions; optional MediaMTX adapter. |
| BudBudness/GUZA_GURA- | main | public | Next.js, TypeScript, Supabase/PostgreSQL, Vercel, PWA; initial scaffold. |
| BudBudness/StramosWisdomCharityOrg | main | public | Next.js/TypeScript/Tailwind frontend, FastAPI backend, PostgreSQL, Docker Compose, GitHub Actions. |
| BudBudness/SMC-Agent- | main | public | Market-structure and SMC intelligence pipeline; evidence ledger, historical analogues and multi-timeframe analysis. |
| BudBudness/Dexta_Buyer_Signal | main | public | Macaly, TanStack Start/React/Vite, Convex, GitHub; public/authorized vehicle buyer-intent intelligence. |
| BudBudness/Ether_Tours-Travel | main | public | Next.js, Supabase/PostgreSQL/RLS, Vercel; enquiry-first travel platform. |

## Verified GitHub access evidence
- Repository listing returned 7 repositories on page 1 and 0 on page 2.
- Owner affiliation listing returned the same 7 repositories.
- Collaborator and organization-member affiliation queries returned no additional repositories.
- Connector metadata reports admin permission flags for all 7 returned repositories.
- A1OS branch `feat/eddie-billions-canonical-control-plane` was created and documentation commits were successfully written; draft PR #22 exists.
- These checks prove access to the listed repositories only, not completeness of all repositories or GitHub organizations.

## Known unresolved repository references
- A1OS/AGENTS.md references BudBudness/a1os-backups (private backup repository); it was not returned in the current seven-repository listing. Direct repository visibility must be tested.
- A1OS/AGENTS.md references .opencode/agents/little-oaks.md and .opencode/agents/security-auditor.md; both paths returned 404 on main and require reconciliation.
- A1OS README.md returned 404; AGENTS.md was accessible.
- Do not run the documented Little Oaks release script as a generic control-plane setup step; it performs acceptance tests, backups, commits, tags and pushes main.

## Cloudflare inventory
**State: BLOCKED — no authenticated Cloudflare management surface available in this session.**

Required fields per account/resource:
- account identifier and account name
- zone/domain or project
- resource type and name/identifier
- environment and owning repository
- bindings/dependencies
- deployment target and current version
- access/permission status
- usage/cost signals
- backup/recovery posture
- observability and health status

Do not record secret values or sensitive credential material.

## Agent capability matrix
| Capability | GitHub Agent | Cloudflare Agent |
|---|---|---|
| Connected identity discovery | PARTIAL — 7 repositories | BLOCKED |
| Read access | VERIFIED — 7 listed repositories | UNVERIFIED |
| Write access | VERIFIED — branch and file commits in A1OS | UNVERIFIED |
| Admin permission metadata | REPORTED for 7 listed repositories | UNVERIFIED |
| Actions/deploy access | UNVERIFIED account-wide | UNVERIFIED |
| Security administration | UNVERIFIED | UNVERIFIED |
| Audit evidence | Partial; this inventory and PR #22 | BLOCKED |

## Required next operations
1. Test direct visibility of BudBudness/a1os-backups and discover any other private repositories.
2. Inspect GitHub Actions workflows, environments, secrets/variables metadata and deployment permissions across all seven repositories without revealing secret values.
3. Discover all Cloudflare accounts, zones and resources using an authenticated account-wide connection.
4. Map resources to projects and environments.
5. Verify each agent's permissions with non-destructive capability checks.
6. Evaluate A1OS as the canonical control-plane host against policy, isolation, security and operational constraints before implementation.
7. Implement enforced tier gates, budgets, recovery and audit.
8. Update this inventory from live evidence; preserve discovery timestamps and evidence references.

## Reporting rule
A domain is COMPLETE only when account scope, pagination, permissions and resource coverage are verified. Otherwise label it PARTIAL, BLOCKED or UNVERIFIED.


## GitHub Actions discovery — 2026-11-05

**Coverage:** workflow directories enumerated for all 7 visible repositories. Recent run history sampled (latest 10 runs per repository). Workflow definitions inspected for representative/operationally significant workflows. Full workflow configuration, repository secrets metadata, environments, deployment protection rules and org-level Actions policy are not yet fully audited; therefore this is a strong partial discovery, not a completed account-wide Actions attestation.

| Repository | Workflow files discovered | Recent run evidence | Findings |
|---|---:|---|---|
| A1OS | 11 | 2,628 total runs; latest three workflows passed on PR #22 branch | Multiple overlapping CI paths: legacy `main.yml`, `ci.yml`, factory DoD, product/vertical E2E workflows. Legacy workflow uses checkout@v3 and broad push trigger. New CI and factory DoD checks passed on PR #22. |
| PyongLive | 8 | 208 total runs; CI, Worker deploy and D1 smoke passed; latest production broadcast E2E failed | Active Cloudflare deployment pipeline; D1 migration/deploy and production E2E. E2E failure remains an operational blocker and requires job-log diagnosis. Separate Cloudflare tokens/permissions are referenced by workflows; secret values were not read. |
| GUZA_GURA- | 1 | 4 total runs; latest main CI success | CI runs typecheck, lint and build; uses npm install rather than npm ci. |
| StramosWisdomCharityOrg | 1 | 25 total runs; latest main CI success | Backend API tests and frontend build are separated into jobs. |
| SMC-Agent- | 4 | 475 total runs; scheduled long-history runs successful | Heavy scheduled pipeline has a 360-minute timeout and contents:write; publishes research artifacts/releases. Requires budget, artifact-retention and least-privilege review before reuse. |
| Dexta_Buyer_Signal | 3 | 423 total runs; intelligence succeeds, buyer pipeline repeatedly fails in latest sample | Scheduled hourly pipeline has contents:write and commits/pushes generated data; investigate repeated failures and tighten permissions/commit behavior. |
| Ether_Tours-Travel | 1 | 56 total runs; recent PR CI mixed, latest sample includes success and failures | Next.js checks typecheck, lint and build; inspect recent failure history before shared policy adoption. |

### Workflow inventory
- A1OS: `a1os-factory-dod.yml`, `car-wash-platform-api.yml`, `car-wash.yml`, `ci.yml`, `legal-production-e2e.yml`, `legal-vertical-ci.yml`, `little-oaks-build.yml`, `little-oaks-production-e2e.yml`, `main.yml`, `production-e2e.yml`, `youtube-high-profit.yml`.
- PyongLive: `ci.yml`, `cloudflare-audit.yml`, `d1-smoke.yml`, `deploy-worker.yml`, `production-e2e.yml`, `pyonglive-d1-schema.yml`, `pyonglive-ops-agent.yml`, `stream-smoke.yml`.
- GUZA_GURA-: `ci.yml`.
- StramosWisdomCharityOrg: `ci.yml`.
- SMC-Agent-: `dashboard-validation.yml`, `long-history-mtf.yml`, `real-data.yml`, `test.yml`.
- Dexta_Buyer_Signal: `intelligence.yml`, `pipeline.yml`, `webapp.yml`.
- Ether_Tours-Travel: `ci.yml`.

### GitHub Actions risk/permission observations
- Workflow files declare `contents: read` in some repositories, but several write-capable workflows explicitly use `contents: write`; inspect every workflow's token scope and trigger trust boundary.
- Dexta Buyer Pipeline pushes generated files to main from a scheduled workflow; verify branch protection, concurrency and bot identity.
- SMC long-history workflow can run for up to 6 hours and publishes large data artifacts/releases; verify spend/runtime limits and data publication policy.
- PyongLive production E2E failure is distinct from successful CI/deploy/D1 smoke runs; do not treat a successful Worker deploy as proof of end-to-end broadcast health.
- GitHub connector's fetch endpoint rejected direct Actions workflow-list and Actions permissions endpoints. Workflow directory enumeration and run history were available. Repository Actions permissions, environments, environment reviewers, secrets/variables names, organization-level policies and deployment protection rules remain unverified.
- No secret values were accessed or copied.

## A1OS control-plane host evaluation — preliminary

**Decision: CONDITIONAL CANDIDATE; do not implement shared automation in A1OS yet.**

Strengths:
- Existing engineering/orchestration repository with Termux operational context and product vertical separation.
- Existing CI and factory Definition-of-Done workflows; both latest PR #22 checks passed.
- GitHub branch/file write capability demonstrated through governance documentation and PR #22.

Risks and gates:
- A1OS is a substantial operational/runtime platform, not a clean isolated control-plane service. Shared automation must be isolated under a dedicated, documented namespace and must not couple to A1OS runtime, task queue, local SQLite state or product verticals.
- Existing workflows overlap (legacy `main.yml`, `ci.yml`, factory DoD and vertical workflows); consolidate only after a full workflow dependency audit. Do not disable or replace existing workflows during this evaluation.
- A1OS operational instructions include scripts with release side effects; shared automation must never invoke release scripts implicitly.
- Prior local inspection recorded an active `data/a1os.db` file with no tables while a separate restored backup passed SQLite integrity. Resolve the runtime database/recovery state independently before treating A1OS as an operationally healthy host.
- Private backup repository visibility remains unresolved.
- Cloudflare account-wide credentials, resources and agent permissions remain unavailable in this session.

Acceptance gates before selecting A1OS:
1. Verify repository/branch protection and workflow permissions, including all write-capable jobs.
2. Resolve A1OS runtime database integrity and documented recovery path.
3. Verify backup repository visibility and restore drill.
4. Define isolated control-plane package, registry schema, audit log and secret boundaries.
5. Demonstrate non-production GitHub + Cloudflare read-only inventory and reversible test deployment without touching product workloads.
6. Document rollback, owner approval gates and recovery evidence.

## Immediate blockers and next operations
1. Establish an authenticated account-wide Cloudflare management/Access surface. Current ChatGPT tool session exposes no Cloudflare management connector; Cloudflare account inventory, Access applications/policies/service tokens, zones and resource permissions cannot be queried or changed from this session.
2. Determine whether the required Cloudflare Access target is (a) Cloudflare Zero Trust Access protecting the control-plane interface and agent endpoints, (b) account-wide Cloudflare API/MCP agent authorization, or both. Do not create broad service tokens or policies until the intended trust boundary and identity model are explicit.
3. Complete GitHub Actions audit: inspect all 29 workflow files, repository/org Actions permissions, environments and protection rules, deployment records, secret/variable names (names only), token scopes, branch protection and recent failure logs.
4. Diagnose PyongLive production E2E and Dexta pipeline failures; review SMC long-running workflow limits.
5. Complete A1OS host acceptance gates before implementation.


### Full workflow-file inspection addendum — 2026-11-05

All **29 workflow YAML files** discovered in the seven visible repositories were fetched and inspected (workflow directory listings plus individual file reads). This completes file-level workflow discovery for the seven visible repositories; it does not complete account/org-wide policy and environment discovery.

Additional findings:
- A1OS production E2E references `A1OS_SUPABASE_URL`, `A1OS_SUPABASE_SECRET_KEY` and `A1OS_EXECUTE_SECRET`. Several production/E2E workflows omit explicit top-level `permissions`; effective default token permissions and job-level overrides must be verified in GitHub settings and workflow execution context.
- A1OS contains pinned action SHAs in some workflows, while others use version tags; standardize supply-chain controls only after reviewing all workflow behavior.
- PyongLive has dedicated Cloudflare audit, D1 schema, operations-agent and Stream smoke workflows. These reference `CLOUDFLARE_API_TOKEN`, `CF_ACCOUNT_ID` and `CF_STREAM_EDIT_TOKEN` by name. The deployment and E2E workflows use additional token names documented above. Values were not accessed.
- PyongLive production deployment has a non-canceling concurrency group, explicit `contents: read`, token verification, remote D1 migration, Worker deploy and HTTP health/events/webhook checks. Production E2E is separately triggered after deployment; latest sampled E2E failed even though deployment and CI succeeded.
- Dexta `pipeline.yml` is an hourly scheduled writer with `contents: write` and a direct push to the checked-out branch. Latest sampled pipeline runs repeatedly failed; investigate before granting broader write capability.
- SMC `long-history-mtf.yml` is a six-hour scheduled research pipeline with `contents: write` and release uploads. The other SMC workflows include dashboard validation, real-data processing and test validation.
- GUZA GURA, Stramos Wisdom Charity and Ether Tours each have one primary CI workflow. GUZA and Ether workflows run typecheck/lint/build; Stramos separates backend tests and frontend build.
- Actions run histories sampled: A1OS 2,628; PyongLive 208; GUZA GURA 4; Stramos Wisdom Charity 25; SMC Agent 475; Dexta Buyer Signal 423; Ether Tours 56. Counts are the API-reported totals at discovery time and may include repeated runs.

**Still outstanding:** GitHub org/account Actions policy, repository Actions permission settings, environment names and reviewer gates, environment secrets/variables metadata, branch protection/rulesets, deployment environment records, reusable workflow dependencies, artifact retention and complete historical failure analysis. The available connector rejected direct reads of Actions permissions/workflow-list endpoints; no secrets values were accessed.


## Cloudflare access architecture decision — approved 2026-11-05

**Owner decision:** implement both Cloudflare Zero Trust Access and scoped Cloudflare API/MCP authorization. They are separate security layers.

### Layer A — Cloudflare Zero Trust Access (human and service ingress)
Protect:
- canonical control-plane web interface and administrative routes;
- remote agent gateways and any private operational endpoints;
- sensitive dashboards and internal tooling.

Baseline:
- default-deny application policies;
- human access through a verified identity provider with MFA;
- distinct policy groups for owner/admin, operator and read-only auditor;
- short-lived sessions and explicit re-authentication for privileged actions;
- service-auth policies for machine-to-machine callers, using dedicated service tokens and rotation;
- no public administrative endpoint without an Access policy;
- log access decisions and administrative events.

### Layer B — Cloudflare API/MCP authorization (resource operations)
- Use dedicated API tokens per automation domain and environment; do not use a Global API Key.
- Start with account/resource read-only inventory permissions.
- Separate write tokens by project and environment (for example PyongLive production versus staging); never share a broad token across unrelated projects.
- Scope tokens to only the necessary account and resource permissions (Workers, D1, R2, Stream, DNS, Access, etc. as required by each registered operation).
- Keep token material in the approved secret manager/GitHub Actions secrets; never in Git, workflow logs, inventory documents or agent prompts.
- Require policy tier checks, target registration, preflight validation, audit evidence and recovery/rollback for writes.
- Treat Access authentication as ingress protection, not as a substitute for Cloudflare API token scopes.

### Identity and trust boundaries
- Human owner identity, human operator identity and machine workload identity must be distinct.
- Access service tokens must not be reused as Cloudflare API credentials.
- API tokens must not be used as interactive login credentials.
- Every request must resolve to a registered project, account, resource and environment before mutation.
- Production and destructive actions remain subject to EB-CAEIO-001 risk tiers.

### Current implementation state
- Architecture decision is approved; no Cloudflare policy, application, service token, API token or resource configuration has been created or changed.
- ChatGPT plugin discovery was performed for Cloudflare account/Access/API management; no eligible Cloudflare plugin was returned.
- No Cloudflare management connector/tool is exposed in the current execution session. Live account discovery and implementation are therefore blocked pending a working authenticated Cloudflare management surface.
- Cloudflare remote MCP endpoint previously identified: `https://mcp.cloudflare.com/mcp`. Its account binding, authentication, available tools and permission scope must be verified from an authenticated client; endpoint existence alone is not proof of connection or access.

### Human identity provider decision — superseded 2026-11-05

The previous Google identity-provider selection and personal Gmail allowlist are withdrawn at the owner's direction. Do not configure Google for this control plane.

### Human identity provider — GitHub approved 2026-11-05

**Owner decision:** Use the owner's existing GitHub identity as the human sign-in provider for the canonical control plane.

Implementation requirements:
- Use Cloudflare Zero Trust's GitHub identity-provider integration.
- Register a GitHub OAuth App. Configure the Cloudflare Zero Trust team domain as the application homepage and use `https://<team-name>.cloudflareaccess.com/cdn-cgi/access/callback` as the callback URL.
- Store the OAuth Client ID and Client Secret only in Cloudflare Zero Trust's identity-provider configuration. Never commit or log them.
- Allow only the verified owner GitHub identity in the initial Access policy. GitHub sign-in alone must not grant access to other users.
- Require GitHub 2FA and test owner login, unauthorized-user denial, recovery and session revocation before enforcement.
- Keep human GitHub identity separate from GitHub Actions credentials, Cloudflare Access service tokens and Cloudflare API tokens.

### Agent authorization — account-wide Cloudflare scope requested 2026-11-05

**Owner request:** Authorize the canonical engineering agents to inspect and operate all resources in the connected Cloudflare account, across registered projects and environments, subject to EB-CAEIO-001.

Implementation requirements:
- Use dedicated Cloudflare API tokens for machine workloads, not the Global API Key.
- Grant the Cloudflare agent account-level read and write permissions for the required resource families across the account, including Workers, Pages, D1, R2, KV, Queues, Durable Objects, Stream, DNS and Zero Trust Access where supported.
- Separate read-only discovery credentials from write-capable credentials; isolate production and non-production credentials where feasible.
- Keep credentials in a secure secret store or protected GitHub Actions secrets; never expose them in Git, logs, prompts or inventory.
- Apply EB-CAEIO-001 risk gates: routine authorized work may proceed autonomously; destructive, irreversible, externally consequential and security-sensitive changes require explicit owner approval and verified recovery.
- GitHub repository permissions and Cloudflare account permissions are separate authorization grants. Do not infer one from the other.

**Implementation state:** The GitHub identity decision and account-wide Cloudflare authorization request are recorded. No OAuth App or Cloudflare identity provider, Access application, policy, API token, account permission or resource configuration has been created or changed. The current execution session exposes GitHub repository tools but no authenticated Cloudflare account-management tool; therefore Cloudflare account authorization cannot be provisioned from this session. Do not claim the agents have Cloudflare access until credentials, scopes and live account access are independently verified.

**Implementation blocker:** the current execution session has no authenticated Cloudflare management connector/tool. Cloudflare configuration cannot be safely inspected or changed until an authenticated management surface is available. Do not claim deployment or access enforcement is active.

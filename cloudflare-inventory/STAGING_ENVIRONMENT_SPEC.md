# Cloudflare Staging Environment Specification

**Status:** Proposed; not provisioned or approved for deployment
**Scope:** Eddie Billions Canonical Engineering Control Plane
**Repository:** `BudBudness/A1OS`
**Target branch:** `fix/pytest-platform-api-import-isolation`

This specification defines an isolated, non-production Cloudflare environment for controlled engineering tests. It is not evidence that staging resources exist, a grant of deployment authority, or approval to provision or incur cost.

## 1. Confirmed facts and proposed architecture

### Confirmed from the current inventory

- The inspected Cloudflare account is `d9be8d8a7f91cb703d7c6210ef413c6a` (`Eddie Billions`). The latest account-list response in the inventory showed only this account; no separate staging account has been verified.
- The accepted account member has the role `Super Administrator - All Privileges`. This does not identify a staging resource owner or authorize staging deployment.
- Read-only lists showed `pyonglive-api`, `pyonglive-db`, and `pyonglive-assets`; these are treated as production resources and are explicitly excluded from staging use and write tests.
- No Pages project or Stream video was returned. Account plan, entitlements, limits, and cost are unknown. No write permission has been tested.
- The inventory records OAuth as the active Cloudflare MCP authentication method. OAuth scope metadata and MCP tool availability are not evidence of a successful write.

### Proposed resource layout

| Resource | Staging design | Non-sharing rule |
|---|---|---|
| Worker | One dedicated staging Worker for the service under test, with a staging-only hostname or private access path. Suggested logical name: `a1os-cp-staging`; confirm naming ownership before provisioning. | No production routes, domains, deployment targets, secrets, or bindings. Do not deploy the staging artifact to the production Worker. |
| D1 | One dedicated staging database for staging schemas and synthetic fixtures. | No production database binding, replication, migration target, customer data, or production export. |
| R2 | One dedicated private staging bucket for test objects and explicitly approved non-sensitive fixtures. | No production bucket, shared credentials, public bucket access, or production objects. |
| KV | Create a separate staging namespace only if application behavior requires KV. If used, bind only that namespace to the staging Worker. | Never bind or read a production namespace. |
| Stream | No staging Stream resource by default. Add a dedicated test resource only after a concrete video test requirement, plan/limit verification, cost approval, and owner sign-off. | No production videos, inputs, keys, or webhooks. |
| Other bindings | Do not add Queues, Durable Objects, Workflows, Analytics Engine, or other products unless a documented test requirement is approved. Any such binding must be a dedicated staging resource. | No production resource IDs or cross-environment service credentials. |

Prefer a separately governed Cloudflare staging account if one is available and approved. Until that is established, account placement is unresolved: the inventory has not verified a separate account. Use of the Eddie Billions account requires explicit account-owner approval and a written isolation review. A shared account does not permit shared resources.

No staging hostname, public DNS record, Pages project, access policy, resource ID, plan, or service limit is selected by this specification.

## 2. Governance and ownership

Use the repository's existing governance concepts:

- `tools/a1os_factory/production_promotion_governance_runtime/README.md` defines validation gates, release approvals, artifact promotion, environment verification, readiness scoring, rollback checkpoints, and governance auditing. Its engine currently generates a promotion manifest; this specification does not assume the runtime automatically enforces Cloudflare controls.
- `tools/a1os_factory/finops_resource_plane/README.md` and `finops_manifest.yaml` describe cost intelligence, budget controls, financial policies, and reporting foundations. They do not define Cloudflare staging budgets or enforce shutdown behavior.

Before provisioning, create a staging registry entry with at least:

| Registry field | Required value |
|---|---|
| Environment and project | Stable environment key (`staging`) and owning A1OS service/project |
| Account and resources | Approved account ID plus exact Worker, D1, bucket, and optional namespace IDs; unknown values remain unset |
| Owner and approver | Named accountable resource owner and separate approver for creation, paid expansion, exposure, and cleanup |
| Purpose and data class | Test purpose, allowed synthetic data class, prohibited data classes |
| Bindings and hostname | Exact staging-only binding IDs and approved hostname/access boundary |
| Cost and usage policy | Approved monthly spend cap, per-resource usage ceilings, alert actions, and suspension method |
| Lifecycle and evidence | Creation approval, deployment commit, validation evidence, backups, rollback owner, expiry/review date, and cleanup record |

**Account and environment boundary**

1. Prefer an account boundary dedicated to staging. If the same Cloudflare account must be used, require a recorded owner decision and explicit resource-ID-level separation.
2. Maintain separate staging and production infrastructure-as-code state, resource identifiers, CI environments, secrets, access policies, logs, backups, and operator procedures.
3. Block deployments when any configured binding, route, hostname, account, or secret is classified as production or is not present in the approved staging registry.

**Least privilege and credentials**

- Use a staging deployment identity limited to the approved staging resources and required operations. Do not use the human Super Administrator session for routine CI deployment.
- Grant read-only access for inspection by default; grant write access only for the resource types and actions required by the approved staging workflow. Do not grant Access revocation, account administration, billing, or production-zone permissions to the staging identity.
- If Cloudflare cannot scope a required permission to the staging resource, record the excess scope and obtain explicit owner/security approval before use; otherwise block deployment.
- Store staging secrets only in the approved secret manager or protected CI environment. Do not place secret values in Git, logs, build artifacts, fixtures, or this registry. Do not copy production credentials or reuse production signing keys, webhooks, API tokens, or database credentials.

**Human approval boundaries**

- Require approval from the resource owner and an independent reviewer before provisioning, external exposure, changing access controls, raising a spend/usage cap, using non-synthetic data, or cleaning up registered resources.
- Require a separate production release approval under the promotion governance process. Passing staging tests does not authorize production promotion.
- No automated job may widen account permissions, create paid services, publish DNS, or promote to production.

## 3. Cost and usage controls

Use free-tier-first configurations where current plan and product documentation confirm eligibility. No Cloudflare price, quota, plan entitlement, or service limit has been verified for this environment; this specification intentionally assigns no invented values.

**Provisioning is blocked until every applicable value below is numeric, owner-approved, and checked against current Cloudflare plan limits:**

| Control | Required before provisioning |
|---|---|
| Monthly spend cap | Maximum approved staging spend in the account billing currency and its monitoring period |
| Worker usage | Request/invocation ceiling and any applicable CPU or scheduled-test ceiling |
| D1 usage | Storage, query/write, and backup/export ceilings supported by the selected plan |
| R2 usage | Stored bytes, object count, operation/request, and transfer ceilings applicable to the selected plan |
| Optional KV/Stream | Product-specific storage, request, processing, and transfer ceilings, if enabled |
| Retention | Maximum lifetime for test data, objects, backups, and logs |

The approved registry must record the provider source/date used to set each service limit. Missing or unsupported caps block that resource from staging.

- Set budget notifications at **50%, 80%, and 100% of the approved staging spend cap**. These are A1OS alert thresholds, not Cloudflare prices or platform limits.
- At 80%, notify the owner and pause nonessential load/soak tests pending review. At 100%, stop test traffic and staging deployments and suspend the staging entry point using a pre-validated, staging-only control. Preserve the data needed for diagnosis and follow the approved recovery/cleanup plan.
- If reliable budget monitoring or a safe, tested staging suspension mechanism is unavailable, the environment cannot be marked operational.
- No unapproved paid plan, feature, add-on, quota increase, or other paid-resource expansion. Expansion requires current pricing/limit review and written approval before use.

## 4. Operations lifecycle

### Provisioning sequence

Provisioning is future work and requires explicit approval; this document performs none.

1. Verify account ownership, staging-account availability, plan/feature eligibility, current product limits, and the staging authorization identity. Record evidence in the registry.
2. Approve the resource owner, reviewer, hostname/access boundary, synthetic-data policy, budget cap, per-resource usage ceilings, retention, alert routing, and suspension mechanism.
3. Create the staging registry entry and independent staging deployment environment before creating Cloudflare resources.
4. Create dedicated D1 and R2 resources, then optional KV only if required. Record returned IDs immediately. Set private access and lifecycle controls before adding data.
5. Create the dedicated staging Worker and bind only those registered staging IDs. Add only staging-specific secrets, after separately approved secure injection.
6. Configure a staging-only hostname or protected access path only after the hostname, certificate/access policy, and DNS ownership are approved. Do not alter production DNS.
7. Deploy an immutable artifact from an approved commit; record the source SHA, configuration digest, resource IDs, approver, and outcome in the audit trail.

Any failed identity, registry, cost, isolation, or permission check aborts before creation/deployment.

### Deployment and health checks

- Separate CI environment, approval rules, state, and credentials from production. Require protected-branch review and a human approval gate for staging release.
- Build once and deploy the reviewed artifact to staging only. The workflow must validate account ID, Worker name, route/hostname, and every binding ID against the registry before deployment.
- Expose only a minimal health/readiness response. It must not reveal secrets, environment variables, customer data, internal diagnostics, or administrative actions.
- Administrative actions must not be available on a public endpoint. Restrict any administrative/test control plane to authenticated, authorized staging operators; deny by default.
- Acceptance tests must cover expected behavior, unauthenticated denial, cross-environment denial, invalid input handling, resource binding isolation, and safe failure behavior. Tests use synthetic data only.
- Record deployment, approval, validation, access-policy, and cleanup events in Cloudflare audit logs where available and in the protected CI/release record. Avoid logging secret values or full user/test payloads.

### Backup, recovery, rollback, cleanup

- Before a schema or test-data change, export/backup staging D1 data and inventory staging R2 objects using the approved, staging-only procedure. Define encryption/access controls and retention from verified provider behavior and policy; do not assume undocumented guarantees.
- Perform a restore drill into a separate staging-only target before the environment is declared operational. Verify schema, row/object counts, and application health without using production resources.
- Application rollback means redeploying the last accepted staging artifact and restoring the previous staging-only configuration. Database rollback requires a verified staging backup/restore or forward-fix plan; Worker rollback does not roll back D1/R2 state automatically.
- Cleanup requires owner approval and an exact registry-ID allowlist. Preview the intended deletions, verify every target has the staging environment label and approved account, then remove only those named resources. Never use broad name patterns or account-wide deletion.
- After cleanup, independently list the account resources and verify the exact staging resources are absent, production resource IDs remain unchanged, staging DNS/access bindings are removed if applicable, and registry/audit records are retained per policy.

## 5. Security requirements

- Synthetic, non-sensitive fixtures only. No production customer data, production backups, production logs, or copied identity records.
- No production credentials, API tokens, signing keys, service tokens, webhooks, or secret values in staging. No staging credential may authorize production operations.
- No production resource sharing: no common Worker, D1, R2 bucket, KV namespace, Stream asset, route, hostname, service token, or binding.
- No public administrative endpoint, open bucket, unrestricted database endpoint, or bypass around Access controls. Public user flows, if later required for acceptance, must be separately reviewed and cannot expose administration or records.
- Deny egress to production control/data endpoints unless a reviewed requirement explicitly allows a narrowly scoped, non-sensitive integration; the default is deny.
- Validate all deployment configuration and generated bindings before release; fail closed on missing IDs, production identifiers, wildcards, or unresolved placeholders.
- Keep secrets out of source, logs, crash reports, artifacts, and this specification. Use separate staging secret names and access groups.

## 6. Verification and operational-readiness gate

Staging may be marked **operational** only when an independent reviewer can inspect evidence for every gate:

1. **Identity and authorization:** Account/environment identity, deployment principal, least-privilege scopes, and successful staging-only read/write operations are recorded. The write test must target a registered staging resource and be independently verified; no production resource may be used.
2. **Resource isolation:** Exact resource IDs and ownership match the registry. Worker configuration and runtime tests prove that D1/R2/optional KV bindings resolve only to staging IDs. Negative tests prove production resource IDs, hosts, credentials, and data are rejected.
3. **Credential isolation:** Secret inventory lists names and owners only, confirms staging-only values, and proves no production credential is available to the staging runtime or CI.
4. **Application acceptance:** Approved smoke, integration, access-denial, and failure-path tests pass against synthetic fixtures. Health checks reveal no sensitive data.
5. **Cost controls:** Approved current-plan usage ceilings, spend cap, alert delivery, threshold behavior, and staging-only suspension are verified before load testing.
6. **Recovery and rollback:** A staging backup is restored successfully; the prior accepted Worker artifact can be redeployed; rollback owners and steps are recorded.
7. **Auditability:** Approvals, artifact SHA, configuration/binding inventory, tests, resource IDs, and results are retained in the audit record.
8. **Cleanup proof:** A cleanup rehearsal or completed test-resource cleanup is independently verified by exact ID. Do not delete the enduring staging environment during ordinary test cleanup.

Missing evidence means **not operational**. Read-only visibility, cached OAuth scope labels, a Super Administrator role description, or MCP tool availability alone is not write authorization.

## 7. Unresolved decisions / blockers

The following require owner or engineering decisions before provisioning:

- Whether a dedicated Cloudflare staging account can be used. The existing inventory identifies one account only; no staging account has been verified.
- Who is the accountable staging resource owner and independent approver.
- Which service/project owns the Worker and whether the Worker serves static assets, API tests, or both.
- The staging hostname and access model. No domain, DNS record, route, or Access app is selected.
- Whether KV is required by the actual staging workload. It remains optional and must be separate if adopted.
- A justified Stream test scenario. None is established by the current inventory or Little Oaks enquiry flow.
- Current account plan, feature entitlements, provider limits/pricing, numeric budget/usage caps, alert destination, suspension mechanism, backup retention, and cleanup expiry.
- A dedicated staging deployment identity and its exact account/resource scopes. Current inventory confirms reads but does not confirm write authorization; `pages.write` was not present as an exact cached OAuth scope label, and no mutation has been tested.

Until these decisions are resolved, the specification is design-only: do not provision resources, deploy code, bind services, import data, or make DNS or permission changes.

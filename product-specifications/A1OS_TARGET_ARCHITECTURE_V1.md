# A1OS Target Architecture V1

**Status:** Proposed target architecture  
**Version:** 1.0-draft  
**Date:** 2026-11-24  
**Platform direction:** GitHub + Cloudflare + Termux  
**Parent:** `product-specifications/A1OS_PLATFORM_SPECIFICATION_V1.md`

> This is a target design, not a description of the current deployed topology. No infrastructure resources are provisioned or changed by this document.

## 1. Architecture objectives

- One shared platform core with independently accessible domain modules.
- Deterministic, auditable execution with AI as an interchangeable capability.
- First-class local execution through Termux and controlled remote execution through Cloudflare.
- Uganda-first mobile-web delivery, UGX commercial support and jurisdiction-aware data handling.
- Clear tenant, data, trust and deployment boundaries.
- Incremental evolution that preserves existing A1OS services and product workloads until individually assessed.

## 2. Logical architecture

```text
Users / Teams / Organisations
             |
     Web Dashboard / CLI
             |
      API and BFF Layer
             |
  Identity / Tenant / Policy
             |
  Shared Platform Services
  | Registry | Knowledge | Billing |
  | Workflow | Audit | Notifications |
             |
       Domain Modules
  | Engineering | Environment |
  | Operations | Research |
  | Automation | Academy |
  | Business | Community |
             |
   Execution and Integration Plane
   | Native deterministic engine |
   | Termux local runner |
   | Cloudflare remote workflows |
   | External AI/agent adapters |
             |
   Evidence / State / Observability
```

The diagram describes logical boundaries. It does not require every box to be a separately deployed service.

## 3. Deployment topology

### GitHub
- Canonical source control, issues, pull requests and review.
- CI for tests, policy, dependency and security checks.
- Release artifacts and signed/tagged provenance where supported.
- Protected environments and required checks for release paths.
- No secret values in source or build artifacts.

### Cloudflare
- Workers for edge API/BFF and suitable application workloads.
- D1 for bounded relational/transactional metadata where workload and limits fit.
- R2 for private documents, learning assets, reports and execution artifacts.
- Queues for asynchronous, retryable work.
- Durable Objects only for workloads requiring coordinated state or real-time sessions.
- KV only for suitable non-authoritative lookup/config/cache use cases.
- Access for staff/admin surfaces where appropriate; consumer identity requires a separately specified application identity/session design.
- Observability, rate limiting and edge security controls.
- Stream only for a justified media/video domain with separate cost and product requirements.

### Termux
- Local development, diagnostics and operator tooling.
- Local A1OS runner for explicitly authorised device-local operations.
- Environment inventory, maintenance and recovery.
- Local project workspaces and test execution.
- Secure local credential references; no secrets in receipts or logs.
- Must remain useful when cloud connectivity is unavailable for local-only tasks.

Cloudflare does not replace Termux for device-local shell access. A Worker must never be assumed to have arbitrary access to the user's Android filesystem or Termux process space.

## 4. Runtime and execution model

### 4.1 Execution classes

| Class | Execution location | Examples | Required controls |
|---|---|---|---|
| Deterministic platform operation | Cloudflare Worker or trusted service | Entitlement check, workflow state transition | AuthZ, schema validation, idempotency, audit |
| Device-local operation | Termux runner | Package inventory, project tests, approved cleanup | Device identity, local policy, command allowlist, approval tier, receipt |
| Remote isolated operation | Dedicated isolated runner/service | Build or analyse untrusted project artifacts | Ephemeral isolation, resource limits, no production secrets, restricted network |
| AI-assisted operation | Approved provider adapter | Research synthesis, code suggestion, classification | Data policy, provider policy, budget, provenance |
| High-impact operation | Appropriate target environment | Production release, DNS/access/credential change | Explicit approval, dual control where appropriate, pre/post evidence and rollback plan |

### 4.2 Native execution engine

The native engine owns:
- Workflow definitions and versions.
- Input/output contracts and validation.
- Policy evaluation and approval requirements.
- Scheduling, retries, timeout and cancellation semantics.
- Idempotency keys and deduplication.
- Execution state transitions.
- Runner selection and capability matching.
- Evidence collection and execution receipts.
- Recovery and reconciliation.

The engine must remain functional without a model provider. AI may propose or parameterise a workflow, but deterministic validation and policy decide whether it can execute.

### 4.3 Termux runner protocol

The local runner should:
1. Register a device/workspace identity without exposing long-lived secrets.
2. Poll or receive only tasks assigned to that runner.
3. Verify task signature, expiry, target, policy version and required approvals.
4. Validate the requested operation against a local capability allowlist.
5. Reject untrusted arbitrary shell commands by default.
6. Execute in a scoped working directory with bounded environment, time and resources.
7. Capture exit status, redacted output, file-change summary and evidence references.
8. Return a signed or authenticated receipt and final state.
9. Support cancellation, lease expiry and safe recovery after interruption.

The cloud control plane must not be able to silently turn a read-only local runner into a privileged shell. Capability grants and approval tier must be explicit and revocable.

### 4.4 Agent adapters

Each provider adapter declares:
- Provider and model identity.
- Supported capabilities.
- Data classification allowed.
- Tool/action permissions.
- Cost and rate limits.
- Timeout and retry policy.
- Provenance and output schema.
- Failure and fallback behaviour.

An agent's output is untrusted input until validated. An agent cannot grant itself permissions, change policy or approve its own high-impact action.

## 5. Shared service boundaries

| Service | Owns | Must not own |
|---|---|---|
| Identity | Accounts, sessions, recovery | Domain-specific business records |
| Tenancy | Organisations, memberships, isolation context | Domain business rules |
| Authorization/policy | Roles, permissions, policy decisions, approvals | UI-only permission checks |
| Registry | Workspaces, projects, modules, resources | Full domain payloads |
| Workflow/execution | Definitions, runs, state, receipts | Provider-specific business logic |
| AI gateway/adapters | Provider routing, budgets, provenance | Authoritative state transitions |
| Knowledge | Documents, sources, versions, search metadata | Unreviewed publication decisions |
| Billing/entitlements | Catalogue, plans, entitlements, invoices, reconciliation | Holding customer funds |
| Integration registry | Integration metadata and credential references | Secret values in ordinary records |
| Audit/observability | Append-only event evidence, metrics, traces | Mutable business source of truth |

## 6. Data architecture

### 6.1 Logical data domains
- Identity and session data.
- Organisation, membership and authorization data.
- Workspace, project and resource metadata.
- Workflow definitions, execution state and receipts.
- Knowledge documents, provenance and learning progress.
- Commercial catalogue, invoices, entitlements and payment events.
- Domain-owned records.
- Security, audit and observability records.

### 6.2 Storage placement

D1 is a candidate for structured metadata and transactional records with bounded size and query patterns. It is not automatically the right store for every domain. High-volume time-series, large analytical scans, binary data, long-running locks and workloads requiring unsupported database features need explicit benchmarking and possibly a different approved Cloudflare-native design.

R2 stores object content; D1 stores metadata, ownership, access and object references. Buckets remain private by default. Signed upload/download flows must be short-lived, scoped and validated.

Queues carry asynchronous work references and idempotency keys, not unrestricted secret-bearing payloads.

### 6.3 Tenancy and authorization
- Every tenant-owned row includes an explicit tenant/organisation scope.
- Query APIs require a verified authorization context.
- Cross-tenant access is denied by default.
- Background jobs carry the original actor, tenant, purpose and authorization snapshot/reference.
- Object storage keys are not treated as authorization.
- Tests must include attempted cross-tenant reads, writes, object access and job replay.
- Platform operators use privileged, audited break-glass access.

### 6.4 Data lifecycle
Every data class defines purpose, owner, collection basis, allowed processors, region/transfer posture, retention, deletion, backup and export rules. Legal retention and deletion conflicts are resolved through documented policy, not ad hoc operator action.

## 7. Identity and access

Use a platform-owned authentication and session design compatible with the approved provider boundary. Do not assume Cloudflare Access is a complete consumer identity solution.

Required controls:
- Secure password hashing if passwords are supported.
- Session rotation, expiry, revocation and device/session listing.
- Rate limiting and abuse detection.
- Recovery flows with anti-account-takeover protections.
- MFA for privileged operators and sensitive organisation roles.
- Least privilege and separation of duties.
- Audited role/permission changes.
- Optional external identity adapters only after explicit provider and privacy review.

## 8. Payments and entitlements

Implement a provider-independent payment interface with provider-specific adapters.

Canonical payment lifecycle:
`created → pending → succeeded | failed | expired → refunded/partially_refunded`

Requirements:
- Verify webhook signatures and provider event identity.
- Idempotently process duplicate and out-of-order events.
- Never grant entitlements based solely on a browser redirect.
- Reconcile provider transactions and settlements.
- Separate payment status from entitlement status.
- Record currency, gross amount, fees, net amount, tax treatment and provider references.
- Protect refund and payout operations with approval and audit.
- Do not store raw card data.
- Confirm recurring mobile-money mandate support provider by provider; do not assume push payments create automatic renewals.

## 9. Academy publishing architecture

Content lifecycle:
`draft → review → approved → published → review_due | withdrawn`

Content records include:
- Author/publisher and responsible organisation.
- Content type and intended learner.
- Learning outcomes and prerequisites where relevant.
- Sources, citations and licence.
- AI assistance/provenance disclosure where appropriate.
- Reviewer and approval evidence.
- Version and review date.
- Accreditation status and evidence, if applicable.

General educational information must remain distinguishable from regulated training. Formal vocational programmes require a separate regulatory gate before sale or delivery.

## 10. Environment maintenance safety model

Maintenance workflow:
`DISCOVER → CLASSIFY → VALIDATE → BACKUP → APPROVE_IF_REQUIRED → EXECUTE → VERIFY → REPORT`

Classes:
- Safe temporary/reproducible cache: may be auto-cleaned only under explicit policy.
- Obsolete build artifacts: verify reproducibility and ownership first.
- Duplicate tools/dependencies: report and propose consolidation; do not remove automatically.
- Unknown files, user data, active project files: preserve.
- Credentials, secrets, keys, tokens and identity material: never inspect values, print, move or delete as routine cleanup.
- System packages, permissions, services and security settings: require impact analysis and approval where change is consequential.

Every maintenance run produces a receipt with inventory digest, classification counts, actions, skipped items, verification results and recovery reference. A successful cleanup is not measured by bytes deleted; it is measured by safe verified improvement.

## 11. API and module contracts

- Version public APIs and domain contracts.
- Use explicit schemas and validation.
- Enforce authorization at the service boundary.
- Use idempotency for mutations that may be retried.
- Use cursor pagination for collections.
- Define stable error codes and correlation IDs.
- Emit structured logs with secrets and sensitive personal data redacted.
- Domain modules declare ownership, routes, events, permissions, data classes, migrations, dependencies and tests in a versioned manifest.

Avoid premature microservices. Begin with a modular monolith or a small set of deployable services with strict module boundaries. Split services only when independent scaling, security, ownership or release cadence justifies the operational cost.

## 12. Security and resilience

Mandatory design controls:
- Threat modelling and secure defaults.
- Secret manager references, never plaintext secrets in Git.
- Dependency pinning, scanning and update policy.
- SAST, dependency and secret scanning in CI.
- Content/file validation and malware handling where appropriate.
- Rate limiting, abuse controls and bot protections.
- Backup encryption, retention and restore tests.
- RPO/RTO targets defined per service and data class.
- Idempotent jobs, dead-letter handling and replay controls.
- Incident response and security event escalation.
- Independent staging and production resources.
- No production deployment based solely on a green unit-test suite.

## 13. Observability and evidence

Every workflow and service should expose:
- Health and readiness.
- Structured logs and correlation IDs.
- Metrics for latency, error rate, throughput and resource use.
- Queue depth, age, retries and dead-letter counts.
- AI/provider cost and usage by tenant and feature.
- Payment reconciliation status.
- Backup freshness and restore evidence.
- Security and authorization denials.
- Execution receipts linked to policy and artifact versions.

An execution receipt records what happened; it is not itself proof that the outcome was correct. Verification evidence must be linked separately.

## 14. CI, release and governance

The repository policy hierarchy remains authoritative. CI must verify:
- Instruction discovery and policy integrity.
- Provider allowlist and dependency boundaries.
- Type, syntax, unit, integration and contract tests.
- Tenant isolation and authorization tests.
- Migration compatibility and rollback.
- Security and secret scanning.
- Cost and resource policy.
- Build artifact provenance.
- Required review and protected environment controls.

Instruction Enforcement V2 is a cross-cutting requirement:
1. Machine-readable policies and approval tiers.
2. Target-aware instruction discovery and preflight.
3. Pre-tool interception where runtime supports it.
4. Independent execution-boundary enforcement.
5. Positive and negative policy tests.
6. Timeout, malformed-input and fail-closed tests.
7. Required branch checks and protected environment reviewers.
8. Tamper-evident execution receipts.
9. Consolidated instruction-gate health reporting.

Hooks are guardrails, not a universal sandbox. The execution boundary must enforce permissions independently of agent instructions.

## 15. Non-functional targets to validate

These are target categories, not yet committed numeric SLAs:
- Availability and recovery objectives per service tier.
- Mobile performance on low-end Android devices and constrained networks.
- Accessibility and responsive behaviour.
- API latency and throughput under representative workloads.
- Tenant isolation and authorization correctness.
- Backup/restore success and recovery time.
- AI cost per workflow and per paying account.
- Payment event processing and reconciliation correctness.
- Audit completeness and retention.

Set numeric SLOs only after workload and user research, baseline measurement and cost modelling.

## 16. Architecture decisions required before implementation

| Decision | Proposed direction | Required evidence |
|---|---|---|
| Application structure | Unified shell + domain experiences | Navigation and task-flow prototype |
| Backend structure | Modular monolith first | Module contracts and deployment constraints |
| Consumer identity | Platform-owned, provider-independent | Threat model and recovery design |
| Primary structured store | D1 where fit is proven | Query, size, concurrency and recovery tests |
| Object storage | Private R2 | Access and lifecycle tests |
| Local execution | Termux runner | Signed task protocol and local safety tests |
| Remote untrusted execution | Isolated runner only | Sandbox threat model and adversarial tests |
| AI integration | Provider adapters | Data policy, budgets and evaluation harness |
| Payment integration | Provider abstraction | Two-provider comparison and sandbox reconciliation |
| Academy regulation | General content separated from formal TVET | Ugandan legal/regulatory review |

## 17. Implementation sequence and gates

1. Reconcile current A1OS code and runtime against this target without modifying production.
2. Define domain manifests, shared contracts, threat model and data classification.
3. Prototype identity/tenant/policy boundaries and prove isolation.
4. Prototype deterministic workflow engine and Termux runner with read-only tasks first.
5. Add execution receipts and approval tiers.
6. Build one end-to-end Engineering or Environment Management workflow.
7. Conduct user testing and measure completion, reliability and cost.
8. Add Academy publishing and commercial capabilities only after their specific regulatory/provider gates.
9. Expand domains only when shared-core contracts remain stable.

**Production remains blocked** until staging isolation, security, cost controls, backup/restore, rollback, independent runtime verification, branch protection, protected environments and explicit release approval are evidenced.

## 18. Architecture status

This document is a reviewable target design. It does not approve:
- Cloudflare resource provisioning or paid expansion.
- Production code changes or deployment.
- Data migration or provider decommissioning.
- DNS, identity, permission or credential changes.
- Payment collection, payouts or refunds.
- Regulated education activity.

Architecture readiness means the design is sufficiently explicit to begin controlled prototypes; it does not mean operational readiness.

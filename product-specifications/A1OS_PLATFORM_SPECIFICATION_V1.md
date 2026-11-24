# A1OS Platform Specification V1

**Status:** Proposed baseline for review  
**Version:** 1.0-draft  
**Date:** 2026-11-24  
**Geographic launch sequence:** Uganda → East Africa → international  
**Repository:** `BudBudness/A1OS`  
**Branch:** `spec/a1os-platform-v1`

> This document defines the intended A1OS product and platform direction. It does not assert that the described capabilities are implemented, legally cleared, commercially validated, or production-ready.

## 1. Product identity

A1OS is an independently governed, extensible operating platform for people and organisations to learn, research, create, build, manage, operate, automate and improve work.

A1OS combines a shared platform core with independently accessible domain experiences. It is not a collection of unrelated applications and is not limited to an AI assistant, coding tool, DevOps product, learning website or business-management application.

**Mission:** Make capable tools, structured knowledge and governed execution accessible to people and organisations, adapting to their skills, resources, devices and operating context.

**Product promise:** One coherent platform; useful domain experiences; shared identity, governance, knowledge, execution and commercial services.

## 2. Product principles

1. **Independent ownership:** One platform and business with unified governance. Domains are product areas, not separate subsidiaries.
2. **Build core once; extend by domain:** Shared capabilities are implemented once and exposed through explicit domain contracts.
3. **Folders and deterministic workflows over agents:** Modules, policies, workflows and contracts are authoritative. AI interprets, analyses and assists; it does not become the execution architecture.
4. **Provider independence:** No single model, AI provider, agent, device or infrastructure vendor owns the platform.
5. **Governance by design:** Identity, permissions, policy, approvals, audit and data boundaries are foundational.
6. **User ownership and portability:** Users can export their information in documented formats, subject to lawful retention and security controls.
7. **Uganda first:** UGX, local payment methods, mobile-first access, local business and learning contexts, and applicable Ugandan law are first-class considerations.
8. **Progressive complexity:** Beginner experiences must not expose unnecessary professional or enterprise complexity.
9. **Low-bandwidth resilience:** Essential workflows should remain usable on constrained mobile devices and unreliable connections.
10. **Evidence-based operation:** No capability is described as verified, reliable, compliant or production-ready without appropriate evidence.

## 3. Audiences and experience model

A1OS serves:
- Individuals and independent learners.
- Beginners and students.
- Professionals and technical practitioners.
- Entrepreneurs and small businesses.
- Teams and institutions.
- Enterprises and public-interest organisations.

The platform adapts onboarding, terminology, defaults, permissions, help and feature exposure to the user's role and demonstrated capability. It must not assume every user is technical.

### Product delivery model

One unified application and dashboard provides global navigation, identity, search, notifications, account settings and cross-domain workspaces. Each domain also has a focused experience that can be entered directly through a stable route or link. Domain experiences reuse shared platform services and do not create independent identity, billing or governance silos.

CLI and dashboard are different interfaces to the same governed capabilities and execution contracts. Neither may bypass platform policy.

## 4. Domain map

Initial domain families:

| Domain | Intended capabilities |
|---|---|
| Engineering | Software, systems and platform engineering; architecture; code; testing; delivery |
| Environment Management | Local development environments, Termux, package/tool inventory, repair, maintenance, backup and recovery |
| Operations | Monitoring, reliability, incidents, deployments, continuity and service operations |
| Intelligence and Research | Research, knowledge discovery, data analysis, evidence management and decision support |
| Automation | Deterministic workflows, scheduling, orchestration, integrations and controlled autonomy |
| Academy | Practical learning, notes, guides, tutorials, learning paths, exercises and assessments |
| Business Operations | Planning, administration, productivity, customer and operational workflows |
| Community and Expertise | Knowledge sharing, collaboration, expert discovery and, later, a governed marketplace |

This is an extensible initial taxonomy, not a closed list. New disciplines must be addable through domain manifests, capability contracts, navigation metadata, policy scopes and tests without redesigning the core.

## 5. Shared platform capabilities

The shared core owns:
- Identity, authentication, sessions and account recovery.
- Individual, team and organisation tenancy.
- Roles, permissions, resource-level authorization and policy evaluation.
- Governance, risk classification, approvals and audit trails.
- User preferences, localisation and accessibility settings.
- Project, workspace and resource registry.
- Workflow definitions, scheduling and orchestration.
- Deterministic execution contracts and execution receipts.
- AI/model/agent provider adapters and usage controls.
- Knowledge, files, provenance, search and retention.
- Integration registry and credential references.
- Billing, products, subscriptions, entitlements and payment reconciliation.
- Notifications, observability, analytics and support operations.
- Export, portability, backup and recovery controls.

A domain may own its specialised business rules and data, but may not independently reimplement shared authentication, tenancy, billing or governance.

## 6. Functional requirements

### 6.1 Identity and organisations
- Support individual accounts and membership in multiple organisations.
- Enforce organisation and resource isolation on every read and write.
- Support role and permission assignment with auditable changes.
- Support secure session expiry, revocation and account recovery.
- Provide a path for non-Google identity options; no Google OAuth dependency is assumed.

### 6.2 Workspaces and projects
- Users can create, organise, search and archive workspaces.
- Resources have explicit owners, visibility, data classification and lifecycle state.
- Domain modules declare the resources and operations they own.
- Cross-domain operations require explicit contracts and authorization.

### 6.3 Execution and automation
- Workflows are versioned, deterministic where possible, idempotent where required and observable.
- Each execution records actor, scope, policy decision, inputs/outputs references, timestamps, status and evidence.
- High-impact operations require approval before execution.
- Retries, timeouts, cancellation, concurrency limits and recovery are defined per operation.
- External agents are replaceable adapters, not trusted authorities.

### 6.4 AI assistance
- Support interchangeable model and agent providers through adapters.
- Apply per-user and per-organisation usage budgets, quotas and cost attribution.
- Make model/provider selection policy-controlled.
- Distinguish model suggestions from executed actions.
- Protect sensitive data from unauthorised provider disclosure.
- Do not use user data for model training unless a lawful, explicit and separately recorded basis exists.

### 6.5 Knowledge and Academy
- Support guides, notes, tutorials, learning paths, exercises and downloadable resources.
- Each published resource has an owner, content type, source/provenance, version, review date and publication status.
- AI-generated material is not automatically trusted or published.
- Clearly distinguish general information, non-accredited learning and formally accredited education.
- Do not claim accreditation, recognised qualifications or formal TVET status without the required authority and approvals.

### 6.6 Commercial capabilities
- Support free access, one-time purchases, subscriptions and organisation plans.
- Entitlements are enforced by the platform, not by UI visibility alone.
- Support UGX-first pricing and payment reconciliation; design for additional currencies.
- Keep payment provider integration behind an adapter.
- Verify provider webhooks and process events idempotently.
- Maintain invoices/receipts, refunds, transaction status and reconciliation records.
- Do not hold customer stored value or operate as a wallet in the initial product.
- Marketplace payouts and revenue sharing are deferred until legal, provider, tax, fraud and dispute controls are established.

### 6.7 Environment management
- Inventory tools, runtimes, packages, versions, dependencies and workspaces.
- Detect configuration drift, conflicts, broken dependencies and abandoned artifacts.
- Classify cleanup candidates before action.
- Automatically remove only policy-approved, verified-safe temporary files and reproducible caches.
- Preserve user data, active project files, unknown files, secrets and credentials.
- Back up before any approved destructive maintenance and verify recovery.
- Produce before/after evidence and an auditable maintenance receipt.

## 7. Commercial model

The initial model is diversified and freemium:

1. Free public knowledge, introductory learning and selected basic tools.
2. Individual paid subscriptions for advanced workflows, AI assistance, workspaces and premium resources.
3. One-time purchases for selected courses, learning packages and specialist resources.
4. Professional services including implementation, training and specialist support.
5. Team and business subscriptions.
6. Enterprise agreements and managed services.
7. Later, a curated expert/content/service marketplace.

All prices are hypotheses until tested with customers and validated against provider fees, tax, support costs, AI consumption and unit economics. Do not encode the earlier indicative price ranges as approved prices.

## 8. Geography, language and accessibility

- Launch commercial assumptions and default currency: Uganda and UGX.
- Design jurisdiction, currency, date, address and tax rules as configurable rather than hard-coded globally.
- East African expansion follows validation of country-specific legal, payment, tax and operational requirements.
- Support responsive mobile-web experiences and progressive enhancement.
- Minimise payloads, provide resumable uploads where appropriate, and support draft/offline queues for suitable workflows.
- Do not claim full offline operation until each workflow has explicit offline semantics and conflict handling.
- Localisation must be quality-reviewed; language support must not be inferred from machine translation alone.

## 9. Trust, safety, privacy and compliance

- Maintain data inventories, purpose, classification, retention and access rules.
- Apply data minimisation and privacy-by-design.
- Assess controller/processor responsibilities, PDPO registration, data-subject rights and international transfers under applicable Ugandan law.
- Maintain vendor and subprocessor records and appropriate agreements.
- Threat-model authentication, tenancy, file handling, payments, AI data flows and code execution.
- Isolate untrusted code and user-supplied content.
- Use least privilege, secure secret storage, encryption, rate limits and abuse monitoring.
- Maintain incident response, breach assessment and notification procedures.
- Obtain legal advice for regulated education, payment aggregation, consumer protection, tax and marketplace activities.

This specification is not a legal opinion or evidence of compliance.

## 10. Explicit exclusions and boundaries

- A1OS will not build or train its own general-purpose foundation model as a prerequisite.
- No single external AI agent is the platform's execution architecture.
- No unapproved hosting, database, identity or CI/CD provider is to be introduced into the canonical engineering control-plane workspace.
- This specification does not authorize migrations or decommissioning of existing product workloads.
- This specification does not authorize production deployments, credential changes, DNS changes, permission changes, payment transactions or infrastructure provisioning.
- No claim is made that the existing A1OS Factory, Platform API or Termux runtime already implements this target state.

## 11. Delivery strategy

Build the platform incrementally, not as eight complete products at once.

| Stage | Outcome | Exit evidence |
|---|---|---|
| S0 — Governance and discovery | Canonical product boundaries, inventory, risk and ownership | Approved specification, current-state map, unresolved assumptions |
| S1 — Core foundation | Identity, tenancy, policy, audit, registry and API contracts | Isolation tests, auth tests, policy tests, migrations and threat model |
| S2 — Execution foundation | Workflow engine, local runner contract, receipts and approvals | Idempotency, retry, cancellation, policy-denial and recovery tests |
| S3 — First domain experiences | Engineering and Environment Management initial workflows | User-tested workflows with measurable completion and safe failure |
| S4 — Knowledge and Academy | Publishing, discovery, learning resources and learner progress | Editorial workflow, provenance and regulatory boundary review |
| S5 — Commercial foundation | Catalogue, checkout, entitlements and reconciliation | Provider sandbox tests, webhook security, refund and reconciliation tests |
| S6 — Business and collaboration | Organisation workspaces, roles, shared work and reporting | Tenant isolation and organisation acceptance tests |
| S7 — Expansion | Additional domains, experts, marketplace and regional support | Separate business, legal, cost and operational release gates |

Stages may overlap only where dependencies and evidence permit. Production release remains separately gated.

## 12. Acceptance criteria for Specification V1

This specification is accepted as a baseline only when:
- Product identity, audiences, principles and domain boundaries are explicit.
- Shared-core ownership versus domain ownership is defined.
- CLI and dashboard use the same policy and execution model.
- Native execution, external agents and local/remote runners have distinct trust boundaries.
- Commercial hypotheses are labelled as hypotheses.
- Uganda privacy, payment and education risks are recorded for legal validation.
- Offline, accessibility, localisation and portability requirements are represented.
- Existing repository workloads and the canonical control-plane boundary are preserved.
- Each delivery stage has evidence-based exit criteria.
- Unresolved assumptions are tracked rather than silently converted into facts.

## 13. Decision and change control

This document is a proposed V1 baseline on a review branch. Material changes to product identity, ownership, domain boundaries, provider policy, data governance, payment model or execution authority require an explicit decision record. Implementation details may evolve without changing the constitution if they preserve these boundaries and pass the relevant acceptance tests.

## 14. Open validation register

The following remain open:
- Customer interviews and willingness-to-pay tests across learner, professional, SME and institutional segments.
- Written provider terms, recurring-payment support, settlement, fees, refunds and sandbox evidence for at least two payment providers.
- Workload-based Cloudflare cost model for 100, 1,000 and 10,000 active users, including AI, media, support and observability.
- Uganda privacy impact and cross-border transfer assessment.
- Legal determination of the boundary between general learning content and regulated TVET provision.
- Security threat model and independent review of untrusted execution.
- Device/network testing and explicit offline behaviour for priority workflows.
- Current-state inventory and migration boundaries for existing A1OS components and product verticals.

**Specification status:** Ready for architecture review; not a production release authorization.

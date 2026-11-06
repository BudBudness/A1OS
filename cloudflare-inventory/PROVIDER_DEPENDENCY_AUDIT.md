# Provider Dependency Audit — Canonical Engineering Control Plane

**Audit date:** 2026-11-06  
**Repository scope:** Seven repositories visible to the connected GitHub account under `BudBudness`  
**Audit branch:** `fix/pytest-platform-api-import-isolation`  
**Audit baseline:** canonical staging specification commit `ca4e192f52a856aae71060615240e289b9ec0485`  
**Status:** Discovery report; no provider configuration, deployments, credentials, data, or infrastructure changed.

## 1. Executive decision

The owner-approved platform boundary for the **Eddie Billions Canonical Engineering Control Plane** is:

- Cloudflare — infrastructure, runtime, storage, data, access and observability.
- GitHub — source control, review, CI/CD and release/audit records.
- Termux — local operator execution and verification.

Vercel, Supabase, Convex, and other unapproved hosting, database, identity, CI/CD, or infrastructure platforms are not permitted as dependencies of the canonical control plane.

This boundary does **not** automatically migrate or decommission independent product workloads. Existing product dependencies are recorded below and must be handled through product-specific architecture and migration plans. No live services or data are to be deleted as part of this audit.

## 2. Repository inventory and findings

Seven repositories were returned by the connected GitHub account listing. The code search covered provider names, SDKs, configuration, environment-variable names, deployment URLs and workflow references; representative files and workflows were fetched for validation.

| Repository | Findings | Classification |
|---|---|---|
| `BudBudness/A1OS` | Root application includes Vercel deployment configuration and cron; runtime task queue switches to Supabase when `VERCEL` is set; Supabase task store and worker use Supabase REST. Product verticals include Legal and Little Oaks Supabase integrations; YouTube High Profit documents Vercel/Supabase. Production E2E workflow targets `a1-os.vercel.app`, requires Supabase secrets and polls Supabase tasks. Legal and Little Oaks E2E workflows use Supabase/Vercel. | **Direct conflict if treated as the control-plane runtime.** Keep product runtime separate; isolate control-plane code and CI from root app runtime. |
| `BudBudness/GUZA_GURA-` | README and architecture specify Vercel + Supabase; package includes Supabase SDKs; browser/server client helpers and Supabase environment variables exist. CI is build/typecheck/lint only; no Vercel deployment workflow was found in the inspected CI file. | Product-specific dependency; not part of control-plane runtime. |
| `BudBudness/Ether_Tours-Travel` | README specifies Vercel + Supabase; package includes Supabase SDKs; server/browser client helpers, environment template and Supabase migration exist. CI builds/tests only in inspected workflow. | Product-specific dependency; not part of control-plane runtime. |
| `BudBudness/SMC-Agent-` | Vercel Next.js configuration and production URL checks; research API directly calls Supabase REST and contains a publishable-key literal; research dashboard persists runs, reports, hypotheses and evidence in Supabase. CI validates the Vercel production endpoints. | Product-specific dependency; not part of control-plane runtime. |
| `BudBudness/Dexta_Buyer_Signal` | Handover documents Vercel frontend and Convex backend (auth/data/functions); owner onboarding uses Google OAuth through Convex Auth. | Product-specific dependency; Convex is also outside the control-plane allowlist. |
| `BudBudness/PyongLive` | Package scripts use Wrangler; dependencies include Cloudflare Workers types and Wrangler. No Vercel/Supabase code-search hits in the current indexed default-branch search. Prior workflow inventory identified Cloudflare Worker deploy, D1 smoke and Stream/broadcast workflows. | **Aligned** with Cloudflare + GitHub. |
| `BudBudness/StramosWisdomCharityOrg` | No Vercel/Supabase code-search hits; package file requested at repository root was not found. Existing workflow inventory identifies GitHub Actions build/test. | No excluded-provider dependency detected in this pass; not a complete runtime attestation. |

## 3. Cross-repository CI/CD observations

The prior workflow inventory enumerated 29 workflow YAML files across these seven visible repositories. The current targeted source inspection confirms:

- A1OS production E2E is coupled to Vercel endpoints and Supabase-backed task execution.
- A1OS Legal and Little Oaks production E2E workflows exercise product-specific Vercel/Supabase integrations.
- SMC-Agent production validation calls its Vercel-hosted production endpoints; its application API persists directly to Supabase.
- GUZA_GURA and Ether Tours CI workflows inspected here perform dependency install, typecheck/lint/build; they do not themselves establish a Vercel deployment.
- PyongLive's intended deployment path is Cloudflare Wrangler through GitHub Actions.
- Dexta's handover identifies Vercel + Convex, but the full workflow set and live project configuration need separate verification.
- Charity's current provider configuration remains partially unverified.

A repository's workflow file or a provider URL is not proof that a current deployment or credential is active. GitHub environment secrets, organization policies, external provider project state, and deployment hooks were not read or changed in this audit.

## 4. Security and configuration notes

- Search results surfaced publishable Supabase client keys embedded in application source for SMC-Agent and A1OS product verticals. These are publishable/client keys, not service-role credentials. Do not treat them as privileged secrets; verify Row Level Security, allowed origins and data exposure. Prefer environment-based configuration to avoid configuration drift.
- No service-role key value or Cloudflare secret value is reproduced in this report.
- A1OS production workflows reference secret names for Supabase and task execution. Secret values were not accessed.
- The canonical control plane must use a separate Cloudflare staging deployment identity and staging-only resources. Product secrets must never be reused.
- Do not bulk-delete environment variables, GitHub secrets, integrations, workflows, provider projects, DNS records or databases based on string matches.

## 5. Required remediation for the canonical control plane

1. Establish a dedicated control-plane namespace/package and dedicated GitHub Actions workflow(s), independent of A1OS root application deployment.
2. Make Cloudflare the only infrastructure/runtime/data provider for the control plane. Keep GitHub as the source and CI/CD authority; Termux as local operator tooling.
3. Add CI policy checks that fail when control-plane paths import Supabase, Vercel, Convex, or unapproved provider SDKs, read unapproved provider environment variables, or reference excluded deployment URLs.
4. Ensure control-plane workflows use explicit minimal GitHub permissions and protected environment gates. Use a dedicated Cloudflare staging identity with resource-scoped permissions where supported.
5. Maintain an explicit provider allowlist and resource registry. Fail closed on unknown providers, account IDs, hostnames, bindings, secrets, and deployment targets.
6. Verify staging Worker/D1/R2 isolation, write permissions, budget limits, access restrictions, audit evidence, backup/restore and rollback before declaring staging operational.
7. Keep existing product deployments untouched until each product receives its own approved migration plan, target architecture, data migration/restore proof, and cutover approval.

## 6. Explicitly out of scope

This audit does not authorize:
- deleting Vercel projects, deployments, domains, DNS, environment variables, tokens or integrations;
- deleting Supabase projects, databases, storage, auth users, migrations, backups, API keys or data;
- removing Convex deployments, functions, auth or data;
- changing production routes, OAuth providers, account roles, GitHub secrets, branch protection or workflow permissions;
- changing any product's runtime architecture.

These are separate, impact-assessed operations requiring explicit approval.

## 7. Coverage limits and next verification gates

- The connected GitHub account returned seven repositories. This is not proof that no additional private, inaccessible, or differently owned repositories exist.
- Code search is indexed and default-branch scoped. It can miss generated files, unindexed branches, submodules, binary artifacts, indirect dependencies, runtime dashboard configuration and secrets.
- Workflow inventory previously sampled 29 YAML files and recent runs; organization-level Actions policy, all environment protections, complete secrets/variables names, deployment integrations and external provider dashboards remain unverified.
- The A1OS repository includes the control-plane governance documents alongside a separate existing application runtime. The control plane must be architecturally isolated from that root runtime before any deployment work.
- Next step: design and implement a provider-boundary CI guard scoped only to canonical control-plane paths; test it against intentionally prohibited references; then create the staging-only workflow. Do not rewrite product workflows or remove provider dependencies from product applications as part of that work.

**Result:** The provider boundary is recorded and the first repository audit is complete at discovery level. The canonical control plane is not yet deployed or operational.

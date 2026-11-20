# Canonical Control Plane — Agent Instructions

These instructions supplement the repository-root `AGENTS.md`, which remains authoritative for shared repository and environment constraints.

## Purpose and platform boundary

Build the Eddie Billions Canonical Engineering Control Plane as an isolated, auditable engineering system.

Approved platform responsibilities:
- **GitHub:** source control, pull requests, review, CI/CD and release/audit records.
- **Cloudflare:** infrastructure, runtime, storage, data, access and observability.
- **Termux:** local operator tooling, execution and verification.

Do not add Vercel, Supabase, Convex, Firebase, Google OAuth, or unapproved hosting, database/backend, identity/authentication, or CI/CD providers as dependencies or execution targets for this control-plane workspace. Update the provider policy and its positive/negative tests when the approved boundary changes.

## Isolation

- Keep implementation under `canonical-control-plane/{src,config,infra,workflows}`.
- Do not couple control-plane CI to product application builds or product-specific provider integrations.
- Do not migrate, rewrite, decommission, or otherwise alter independent product workloads as part of control-plane work.
- Keep product-specific workflows and runtime architecture outside this workspace unless separately approved.
- Treat provider-policy scan scope as deliberate; do not broaden it silently.

## Execution and safety

- Inspect the target branch, working tree, current configuration and relevant resource state before changes.
- Preserve all unrelated work. Never reset, clean, force-push, rebase over, or discard existing work.
- Routine read-only inspection, implementation, static checks and tests may proceed without per-step approval.
- Obtain explicit approval before destructive or irreversible changes, production changes, external consequences, security-sensitive changes, or credential/permission/access-policy modifications.
- Never print, commit, or expose secrets, credentials, tokens, private keys, or environment files.
- Use dedicated staging resources and identities; never reuse production credentials or bindings.
- Do not deploy or modify live resources merely because CI passes.

## Quality and release gates

- Add deterministic tests for policy behavior, including both prohibited and approved examples.
- Run the narrowest relevant tests, then applicable repository CI checks.
- Distinguish static-policy success from implementation, staging, runtime, and release readiness.
- Do not claim readiness until application implementation, isolated staging, authorization, cost controls, backup/restore, rollback and independent verification are evidenced.
- Record unresolved gaps explicitly.

## Delivery

Report changed files, commits/PRs, tests and actual results, readiness state, and outstanding blockers. Do not claim unperformed work.

# Canonical Engineering Control Plane

This directory is the isolated implementation boundary for the Eddie Billions Canonical Engineering Control Plane.

## Approved platform boundary

- Cloudflare: runtime, infrastructure, data, storage, access and observability.
- GitHub: source control, review, CI/CD and release records.
- Termux: local operator tooling and execution.

Vercel, Supabase, Convex, and any other unapproved provider are prohibited as dependencies or execution targets in this workspace. Product code elsewhere in this monorepo is outside this guard's scan scope and is not changed by this policy.

## Directory contract

- `src/`: control-plane application and library source.
- `config/`: provider/resource allowlists and non-secret configuration.
- `infra/`: Cloudflare infrastructure definitions.
- `workflows/`: reusable control-plane workflow definitions, if needed.

Do not place secrets in this directory. Use protected GitHub environments and a dedicated staging deployment identity. Never reuse production credentials or bindings.

## Enforcement

`.github/workflows/canonical-control-plane-policy.yml` runs a deterministic provider-boundary check against the directories above. The guard is intentionally scoped to this workspace; it does not rewrite or block unrelated product workflows.

The control plane remains design/development-only until staging resource isolation, authorization, cost controls, backup/restore, rollback and independent verification gates are satisfied.

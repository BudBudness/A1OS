# Canonical Engineering Control Plane

This directory is the isolated implementation boundary for the Eddie Billions Canonical Engineering Control Plane.

## Approved platform boundary

- Cloudflare: runtime, infrastructure, data, storage, access and observability.
- GitHub: source control, review, CI/CD and release records.
- Termux: local operator tooling and execution.

Unapproved hosting, database/backend, identity/authentication and CI/CD providers are prohibited as dependencies or execution targets in this workspace. Product code elsewhere in this monorepo is outside this guard's scan scope and is not changed by this policy.

The machine-readable provider inventory is `config/provider-policy.json`. The static guard currently has explicit detection rules for Vercel, Supabase, Convex, Firebase, Auth0, Clerk, Okta, Keycloak, WorkOS and Google OAuth. Adding another dependency class requires a policy update and positive/negative tests.

## Directory contract

- `src/`: control-plane application and library source.
- `config/`: provider/resource allowlists and non-secret configuration.
- `infra/`: Cloudflare infrastructure definitions.
- `workflows/`: reusable control-plane workflow definitions, if needed.

Do not place secrets in this directory. Use protected GitHub environments and a dedicated staging deployment identity. Never reuse production credentials or bindings.

## Enforcement

`.github/workflows/canonical-control-plane-policy.yml` runs:
- guard self-tests for each prohibited dependency class;
- unit tests for prohibited imports, endpoints, environment variables and deployment actions;
- positive tests for approved Cloudflare/GitHub references;
- comment-handling and empty-workspace tests;
- the scoped provider-boundary scan.

The guard inspects only `canonical-control-plane/{src,config,infra,workflows}`. It deliberately does not scan or rewrite product directories or unrelated workflows.

## Readiness status

A passing provider-boundary scan is not a runtime or deployment-readiness approval. An empty scan reports `NO_IMPLEMENTATION`. The control plane remains design/development-only until an application exists and staging resource isolation, authorization, cost controls, backup/restore, rollback and independent verification gates are satisfied.

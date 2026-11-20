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


## Enforcement scope and limitations

The initial CI guard is a deterministic denylist for the currently identified excluded providers: Vercel, Supabase and Convex. It is not yet a complete general-purpose allowlist for arbitrary third-party packages, URLs or services. The guard's passing result must not be interpreted as proof that every unknown provider is blocked. Before adding control-plane dependencies, review the provider inventory and extend the guard with explicit tests for the proposed dependency class. The workspace currently has no production application implementation; an empty scan is not evidence of runtime or deployment readiness.


## Agent instruction and release enforcement

- `.github/copilot-instructions.md` requires repository and scoped instruction discovery before work.
- `scripts/control-plane/check_agent_instructions.py --check` validates the canonical hierarchy and rejects known contradictory provider mandates.
- `--preflight --for-path <path>` prints the complete applicable instruction chain with SHA-256 digests. CI captures this output before running the control-plane checks.
- `--working-copy <path>` compares instruction-file hashes against the canonical checkout. Repeat the option for every local checkout that must be audited.
- `--global-instructions <path>` checks the operator's global instruction file for the canonical platform and approval boundaries.
- `scripts/control-plane/check_release_gates.py --evaluate` fails closed until every required gate has verified evidence. The checked-in manifest deliberately keeps production deployment disabled and release BLOCKED.

A GitHub Actions preflight proves that the CI runner loaded the applicable files; it does not, by itself, prove that every external agent runtime obeys them. Agent integrations must invoke the preflight before starting work and retain its output as execution evidence. Local Termux worktrees and the operator's global instruction file must be checked from the Termux host because GitHub cannot inspect files stored only on that device.

Branch protection / required-check settings and GitHub environment reviewer rules are repository settings, not source files. The workflow check is not a mandatory merge gate until those repository settings require it.

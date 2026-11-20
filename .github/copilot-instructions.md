# Repository-wide Copilot instructions

Before any inspection, planning, editing, command execution, test run, or tool action:

1. Read the repository-root `AGENTS.md`.
2. For work under `canonical-control-plane/`, also read `canonical-control-plane/AGENTS.md`.
3. Run the deterministic instruction check:
   `python3 scripts/control-plane/check_agent_instructions.py --check`
4. Load and print the applicable instruction chain before execution:
   `python3 scripts/control-plane/check_agent_instructions.py --preflight --for-path <target-path>`

Do not begin the requested task if preflight fails. Apply all applicable instructions cumulatively; a scoped instruction supplements the root contract and cannot override security or approval boundaries. If instructions conflict, stop and report the exact conflict rather than choosing the more permissive rule.

Canonical engineering platform: GitHub + Cloudflare + Termux. Do not add Vercel, Supabase, or another unapproved provider to the canonical control-plane workspace.

Routine read-only inspection, implementation, and deterministic tests are authorized. Obtain explicit approval before destructive or irreversible changes, production changes, external-consequence actions, security-sensitive changes, or credential, permission, identity, DNS, or access-policy changes.

Never claim that an agent loaded instructions unless the preflight output or an execution receipt is available as evidence. Never claim deployment or runtime readiness from static checks alone.

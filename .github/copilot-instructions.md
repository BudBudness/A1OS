# Repository-wide Copilot instructions

Before any inspection, planning, editing, command execution, test run, or tool action:

1. Read the repository-root `AGENTS.md`.
2. For work under `canonical-control-plane/`, also read `canonical-control-plane/AGENTS.md`.
3. Run the deterministic instruction check:
   `python3 scripts/control-plane/check_agent_instructions.py --check`
4. Load and print the applicable instruction chain before execution:
   `python3 scripts/control-plane/check_agent_instructions.py --preflight --for-path <target-path>`

Do not begin the requested task if preflight fails. Apply all applicable instructions cumulatively; a scoped instruction supplements the root contract and cannot override security or approval boundaries. If instructions conflict, stop and report the exact conflict rather than choosing the more permissive rule.

Repository platform: GitHub + Cloudflare + Termux. Vercel and Supabase are retired across this repository. Do not add new dependencies, deployments, credentials, cron jobs, or CI integrations for either. Existing product integrations must be migrated and verified before their remaining code or data is removed.

Routine read-only inspection, implementation, and deterministic tests are authorized. Obtain explicit approval before destructive or irreversible changes, production changes, external-consequence actions, security-sensitive changes, or credential, permission, identity, DNS, or access-policy changes.

Never claim that an agent loaded instructions unless the preflight output or an execution receipt is available as evidence. Never claim deployment or runtime readiness from static checks alone.

## Enforced agent startup and tool gate

This repository ships a GitHub Copilot hook at `.github/hooks/a1os-instruction-guard.json`.

- `sessionStart` runs the deterministic preflight and injects the verified repository and scoped instruction chains into the agent context.
- `preToolUse` re-runs the full instruction validator before every tool call. If the repository root cannot be located, the checker fails, or policy drift is detected, the hook returns a deny decision.
- A successful hook returns no permission decision; it does not grant tool permissions or bypass Copilot's normal approval model.
- Keep the hook configuration and guard script on the repository default branch. Copilot cloud agent only loads repository hook configuration from the default branch.
- If a runtime does not support repository hooks, run the documented `--check` and `--preflight --for-path <target-path>` commands manually before any work. Do not claim automatic enforcement for unsupported runtimes.

Hook timeout limitation: GitHub documents command-hook timeouts as fail-open for `preToolUse`. Keep the guard fast, retain the per-tool validation, and treat hook execution evidence as required. This hook enforces supported Copilot CLI/cloud-agent sessions. Internal A1OS agent entrypoints also invoke the deterministic preflight directly. It does not control unrelated external agent runtimes.

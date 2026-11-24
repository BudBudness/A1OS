# Repository-wide Copilot instructions

Before any inspection, planning, editing, command execution, test run, or tool action:

1. Read the repository-root `AGENTS.md`.
2. For Claude Code only, `CLAUDE.md` imports the canonical root policy; Copilot must not treat Claude-specific settings as Copilot configuration.
3. For work under `canonical-control-plane/`, also read `canonical-control-plane/AGENTS.md`.
4. Run the deterministic instruction check:
   `python3 scripts/control-plane/check_agent_instructions.py --check`
5. Load and print the applicable instruction chain before execution:
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
- Codex project hooks load only from a trusted project layer. On the local Codex CLI, inspect and trust the repository hook through `/hooks`; if the project layer is not trusted or hooks are disabled, use the documented `--check` and `--preflight --for-path <target-path>` commands manually. Do not claim automatic enforcement until the hook is loaded.

Hook limitation: GitHub documents command-hook timeouts as fail-open for `preToolUse`; Codex documents that pre-tool hook errors, timeouts, malformed responses, and some specialized tool paths can allow execution. The guard uses a 10-second internal timeout beneath each runtime’s 30-second hook timeout, but it is a runtime guardrail rather than a universal sandbox. Keep the guard fast and treat hook execution evidence as required. This hook enforces supported Copilot CLI/cloud-agent sessions. Internal A1OS agent entrypoints also invoke the deterministic preflight directly. It does not control unrelated external agent runtimes.


## Termux environment operations

Use `scripts/termux-maintenance/a1os_termux_maintenance.py` for the supported read-only inventory and guarded cache maintenance. Read `docs/TERMUX_ENVIRONMENT_MANAGEMENT.md` before using cleanup. Never broaden the allowlist or add scheduled deletion without a separately reviewed change. CI self-tests do not prove the Android Termux host was inspected or repaired.

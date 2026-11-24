# Claude Code instructions for A1OS

@AGENTS.md

## Claude Code operating contract

- Treat the imported repository-root `AGENTS.md` as the authoritative engineering, safety, architecture and approval policy.
- Before work, run:
  `python3 scripts/control-plane/check_agent_instructions.py --check`
  and
  `python3 scripts/control-plane/check_agent_instructions.py --preflight --for-path <target-path>`.
- For work under `canonical-control-plane/`, the preflight chain must include `canonical-control-plane/AGENTS.md`.
- Do not infer that hooks are active. Verify Claude Code hook configuration and execution evidence before claiming enforcement.
- Use deterministic commands and tests before delegating work to subagents. Subagents inherit the same policy and must not broaden permissions.
- Do not use Claude API tokens or paid API access when an authenticated Claude Code subscription/session is already available. Do not bypass provider authentication, licensing, usage limits, or access controls.
- Preserve project state. Never run broad cleanup, reset, force-push, production deployment, secret rotation, or permission changes without the approvals required by `AGENTS.md`.
- Report concrete files, commits, test results, evidence, limitations and outstanding gates. Never claim local Termux execution unless it was actually run on the Termux host.

## Runtime-specific notes

Claude Code is an execution adapter, not an owner of A1OS policy or project state. Keep durable instructions in `AGENTS.md`; keep this file limited to Claude Code discovery and runtime-specific behavior. Copilot-specific hooks and settings remain in `.github/`, and Codex-specific configuration remains in `.codex/`.

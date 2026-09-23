# A1OS

A1OS is a deterministic platform/control plane with a lightweight Product Factory. The platform owns shared runtime concerns; product verticals own frontend experiences and explicit workflows.

## Architecture
- Core/platform: runtime, auth, tenancy, authorization, RBAC, persistence, security, execution controls, deployment, governance, evidence and recovery.
- Product Factory: 37 lightweight, composable deterministic engines.
- Vertical products: customized frontend products generated from explicit requirements.
- AI: interpretation and analysis only; application logic, validation, authorization and execution remain explicit code/workflows.
- Principle: folders over agents.

## Factory
Every roadmap engine is implemented as a callable deterministic contract using the shared factory runtime. The vertical generator materializes only frontend-owned structure and records platform-owned responsibilities in its manifest.

## Validation
Run:
- python3 -m compileall .
- python3 -m pytest -q
- python3 tools/a1os_factory/final_definition_of_done.py

A release is complete only when all three pass.

## Security
Execution is explicit, scoped and approval-gated. The control plane uses an allowlist and create_subprocess_exec; arbitrary shell strings are not accepted. Secrets and environment-specific credentials remain outside source control.

## Development
Use the Termux Python environment for local validation. Do not run release scripts that commit or push to the default branch without explicit authorization.

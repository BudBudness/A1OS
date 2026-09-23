# A1OS Product Factory — Definition of Done

The Product Factory is complete only when all 37 engines are implemented and evidence-producing, the generated products are lightweight and customized from explicit requirements, and the platform enforces deterministic execution.

## Non-negotiable architecture
- Folders/modules/workflows are authoritative.
- AI may interpret or analyze but does not become the execution architecture.
- Generated verticals do not own platform authentication, tenancy, RBAC, persistence or infrastructure.
- JARVIS and MCP are not part of the architecture.

## Engine contract
Every engine must:
1. expose a deterministic callable/CLI entrypoint;
2. accept explicit product requirements;
3. produce a machine-readable contract/manifest;
4. be safe to compose with other engines;
5. be covered by automated validation.

## Product contract
Generated products are intentionally lightweight and customized. The factory creates only the folders and capabilities requested by the product requirements.

## Evidence
`final_definition_of_done.py` is the release gate. CI runs compilation, factory tests and the final audit.

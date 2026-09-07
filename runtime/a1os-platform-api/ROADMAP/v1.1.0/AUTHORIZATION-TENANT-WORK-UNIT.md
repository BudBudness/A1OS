# A1OS v1.1 — Authorization + Tenant Isolation Work Unit

## Baseline

- Frozen baseline: `A1OS-v1.0.0-verified`
- Development branch: `a1os-v1.1-development`

## Required gates

1. Authorization enforcement audit
2. Permission denial regression
3. Role boundary regression
4. Super-admin behavior regression
5. Tenant isolation regression
6. Cross-organization read denial
7. Cross-organization mutation denial
8. Audit/event recording verification
9. Python syntax
10. API import
11. Runtime health
12. Runtime readiness
13. Database integrity

## Rules

- No cross-tenant data access.
- No authorization bypass through alternate endpoints.
- Preserve super-admin platform semantics.
- Do not weaken authentication.
- Do not modify the frozen v1.0.0 tag.
- Do not commit or tag v1.1.0 until all gates pass.

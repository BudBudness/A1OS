# Cloudflare account and Little Oaks zone inventory

**Captured:** 2026-11-06 08:23 UTC  
**Requested zone:** `littleoaksmontessori.ug`  
**Inventory status:** **OAuth authenticated; account identity and selected account resources verified read-only.** This report distinguishes repository configuration from live Cloudflare resources. Unknown resources are not assumed absent.

## Authentication and scope

- **Authentication method:** Cloudflare MCP OAuth at `https://mcp.cloudflare.com/mcp`; the active `.mcp.json` entry is HTTP transport and contains no API-token credential configuration.
- **OAuth evidence:** MCP `whoami` succeeded as `eddiebillions85@gmail.com` (user ID `b47ebe061689f9d470d8105c041a36a5`). The local Copilot diagnostics record successful Cloudflare OAuth authentication and subsequent MCP client initialization. OAuth cache metadata is present; credential values were not inspected or exposed.
- **Live API evidence:** Read-only account-detail, membership, Workers, Pages, D1, R2, Stream, Access applications, and Access policies requests all returned successfully for account `d9be8d8a7f91cb703d7c6210ef413c6a`.
- **API-token verification:** **Not applicable** to this OAuth session. `/user/tokens/verify` is an API-token verification endpoint and was not used as an OAuth health check.
- Account membership is accepted with role `Super Administrator - All Privileges`. This is role evidence, not proof that every mutating API operation has been individually tested.
- No writes, deployments, deletions, revocations, DNS changes, or permission changes were attempted. The requested zone is verified as present from the current account inventory in earlier read-only inspection; DNS record contents and current zone configuration were not queried in this update.
- No resources were created, changed, deployed, deleted, or provisioned. No DNS or nameserver changes were made.

## Selected live account resource access (read-only)

The following results are live API responses for account `d9be8d8a7f91cb703d7c6210ef413c6a`:

| Category | Observed resources |
|---|---|
| Account | `Eddie Billions` (`standard`) |
| Membership | `eddiebillions85@gmail.com`, accepted, `Super Administrator - All Privileges` |
| Workers | `pyonglive-api` |
| Pages | List request succeeded; 0 projects |
| D1 | `pyonglive-db` |
| R2 | `pyonglive-assets` |
| Stream | List request succeeded; 0 videos |
| Zero Trust Access | 1 application (`wispy-base-31b4 - Cloudflare Workers`); 3 reusable policies |

These are observed list results, not a complete inventory of all Cloudflare products.

## Write-capability discovery

- Cloudflare API OpenAPI metadata exposes write operations and their required API permission groups (for example Workers Scripts Write, Pages Write, D1 Write, Workers R2 Storage Write, Stream Write, and Access Apps and Policies Write). MCP exposing an execute tool does not prove that these operations are authorized.
- Cached OAuth scope labels include write scopes for Workers scripts, D1, R2, Stream, Access, Access policies, Access service tokens, account settings, and DNS. The exact `pages.write` scope label was not present (the cache includes `page.write`, which is not the same label). Scope metadata is not a successful write test or proof of Cloudflare endpoint authorization.
- **Write permissions actually tested: none.** No write operation was called.
- **Non-production target: none verified.** The current resource lists show PyongLive Worker/D1/R2 resources, which are excluded from testing. The repository architecture-gap document discusses an isolated staging deployment as a future step, but provides no existing target identifier, isolation proof, target ownership, or rollback procedure.
- Consequently, write testing stopped before any mutation. A suitable target requires a specifically registered non-production resource with owner confirmation, isolation from production, and a documented cleanup/rollback path.

## Persistence and validation

- Initial verified inventory commit: `bbbd1c37c89a8861394389c37dc84a2bbf98256d` on `fix/pytest-platform-api-import-isolation`.
- Push verification: GitHub remote `origin` reported the same SHA for `refs/heads/fix/pytest-platform-api-import-isolation`.
- Validation: JSON parsing passed; staged inventory diff contained only the JSON and Markdown inventory files; credential scan found no bearer credentials, private keys, or credential assignments.
- Authorization-test result: **not run** because no registered isolated non-production target, owner confirmation, and rollback procedure were available. No production resource was used.

## Requested Little Oaks live inventory

| Category | Result |
|---|---|
| Account plan and entitlements | Unknown — not queried. Do not infer Workers Paid, Containers, D1, Queues, Workflows, R2, or Pages entitlements from list visibility. |
| Workers and deployed scripts | Unknown remotely. Repository configuration contains `a1os-health-checker`; deployment status is unverified. |
| D1 databases, IDs, migrations | Unknown remotely. No Little Oaks Cloudflare D1 binding or migration is evidenced by the inspected repository configuration. |
| Queues and consumers | Unknown remotely. No queue producer/consumer binding is evidenced by the inspected Wrangler configuration. |
| R2 buckets | Unknown remotely. No R2 binding is evidenced by the inspected Wrangler configuration. |
| Workflows | Unknown remotely. No Workflow binding is evidenced by the inspected Wrangler configuration. |
| Containers and availability | Unknown remotely. No Container binding/configuration is evidenced by the inspected Wrangler configuration; plan availability is unverified. |
| Pages projects and deployments | Unknown remotely. The Little Oaks repository has Vercel build configuration and a production E2E URL, which do not prove any Cloudflare Pages project exists. |
| DNS records, proxy status, nameservers | Not queried in this update. No DNS record should be inferred from application canonical URLs or local tunnel configuration. |
| Worker bindings, routes, environment configuration | Unknown remotely. Local `a1os-health-checker` configuration is summarized below; it does not prove that the Worker or its bindings exist in the account. |

## Repository evidence (not live account evidence)

The only checked-in Wrangler configuration found is `cf-workers/a1os-health-checker/wrangler.jsonc`. It names Worker `a1os-health-checker`, uses `src/index.ts`, schedules a five-minute Cron, configures an Analytics Engine dataset binding `HEALTH_EVENTS` for `A1OS_HEALTH_EVENTS`, enables observability, and declares `HEALTH_STATE` KV binding IDs as `REPLACE_WITH_KV_NAMESPACE_ID`. The file's comments describe creating resources and deploying; they are not deployment evidence. There is no Little Oaks-specific Wrangler configuration in the repository.

Little Oaks evidence:

- `products/verticals/little-oaks/vercel.json` builds a Vite site to `dist`.
- `.github/workflows/little-oaks-production-e2e.yml` targets `https://little-oaks-one.vercel.app` and expects the browser enquiry request to POST to `/rest/v1/enquiries`.
- `products/verticals/little-oaks/src/App.jsx` sends the enquiry directly from the browser to Supabase, then opens WhatsApp after a successful response.
- `products/verticals/little-oaks/A1OS_DEPLOYMENT.json` identifies the product's API, authentication, tenancy, authorization, and RBAC providers as A1OS platform services.
- `products/verticals/little-oaks/index.html` and its sitemap use `littleoaksmontessori.ug` as the canonical public domain. This is not proof of current DNS configuration.
- `AGENTS.md` documents a separate A1OS tunnel hostname, `little-oaks.pyongcity.org`, routed to local services. It is not evidence that the requested `littleoaksmontessori.ug` zone is configured or should share those routes.

## Verification limitations

Read access to the selected account endpoints is verified through OAuth. The complete Little Oaks account/zone inventory remains incomplete: plan/entitlements, DNS records, Worker bindings/routes, and several product lists were not queried in this update. The membership role is broad, but no write or delete authorization was tested. No registered, isolated non-production target with an owner and rollback procedure was found, so no write test was attempted. Do not treat OAuth scopes, MCP tool availability, or a successful GET as proof that a mutation is authorized.

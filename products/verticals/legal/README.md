# Barya, Byamugisha & Co. Advocates — Internal Legal Practice Platform

A1OS vertical for governed internal practice operations: matters, clients, deadlines, tasks, documents, billing, research and audit.

## Approved runtime

- **Frontend:** Vite + React, static assets served through Cloudflare.
- **Identity:** Cloudflare Access; the Worker verifies the Access JWT signature, issuer and application audience. Staff must also have an active Legal profile in D1.
- **API and authorization:** Cloudflare Worker.
- **Relational data:** Cloudflare D1 (SQLite).
- **Documents:** private Cloudflare R2 bucket; the API checks matter membership before serving an object.
- **Source and release:** GitHub + GitHub Actions; operator tooling may run in Termux.

No Supabase, Vercel, browser-held database credentials, or direct browser-to-database access.

## Provisioning gates

1. Create a D1 database named `barya-legal` and an R2 bucket named `barya-legal-documents`.
2. Replace the D1 database ID, Access team domain and Access application audience in `worker/wrangler.toml`.
3. Apply `worker/migrations/0001_initial.sql` with Wrangler.
4. Configure a Cloudflare Access self-hosted application for the frontend/API hostname and set its audience.
5. Provision active staff profiles in D1 using verified Cloudflare Access subject IDs and firm-approved roles. Do not self-register users or grant roles from browser input.
6. Deploy the Worker and static frontend; configure the route so `/api/*` reaches this Worker and the SPA assets are served from Cloudflare Pages or the approved static hosting path.
7. Verify access-denied, matter-isolation, document upload/download, backup and restore before production use.

## Local verification

From this directory, run `npm install && npm test && npm run build`. From `worker/`, run `npm install && npm test`.

## Data recovery

The former Supabase project was deleted before export verification. This migration does not recreate deleted records. Import a verified, authorized backup into D1 before enabling production users. Never seed invented client or matter data.

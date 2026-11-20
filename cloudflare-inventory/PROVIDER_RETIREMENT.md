# Vercel and Supabase retirement — A1OS and portfolio audit

## Canonical platform

The approved platform direction is GitHub + Cloudflare + Termux. Vercel and Supabase are retired providers. Do not add new integrations, deployments, credentials, cron jobs or CI dependencies for either provider.

## External decommissioning — verified

- Vercel project inventory returned zero projects after the owner's manual deletion.
- Supabase project inventory returned zero projects after the owner's manual deletion.
- Owner confirmed that the Vercel and Supabase GitHub Apps were removed from repository access.
- These are account-level changes; this document records the verification and owner confirmation, not an automated uninstall operation.

## A1OS repository changes in PR #49

- **YouTube High Profit:** all 23 product files and the dedicated workflow removed from the PR branch. No product code is being migrated; the product is being retired.
- **Legal:** browser Supabase SDK, credentials, password-auth flow and direct database calls removed from the PR branch. Replaced with Cloudflare Access JWT verification in a Worker, D1 relational persistence, matter-membership authorization, audit events and private R2 document storage.
- **Frontend and Worker:** GitHub Actions frontend tests/build, Worker tests, local D1 migration application and Wrangler deploy dry-run passed.
- **Historical Supabase migrations:** root `supabase/migrations/` files are retained as immutable audit/migration evidence only. They are not executable runtime dependencies.

## Legal production gates — still open

- Create the D1 database and R2 bucket in the Cloudflare account.
- Set the exact Access team domain and application audience; configure the Access application and staff policy.
- Replace the placeholder D1 database ID in Wrangler configuration.
- Provision staff profiles from verified Access subject IDs and assign matter memberships.
- Deploy the combined Worker + Workers Assets bundle.
- Import data only if a verified, authorized export exists. Prior context search found no recorded Legal database export, backup or restore evidence before the former Supabase project was deleted. The earlier Legal artifact was described as a generated/orchestrated skeleton, not a verified live persistence system.
- Complete live browser, access-denied, matter-isolation, document upload/download, backup and restore tests.

No production runtime is declared migrated until those gates pass.

## Additional repository findings

A portfolio-wide GitHub code search found further Vercel/Supabase references outside the two A1OS products in this PR:

- `BudBudness/Ether_Tours-Travel`: Supabase SDK/auth/database code and Vercel deployment assumptions.
- `BudBudness/GUZA_GURA-`: Supabase SDK/auth/database code and Vercel deployment assumptions.
- `BudBudness/SMC-Agent-`: Vercel configuration and direct REST calls to the deleted Supabase project URL.

These repositories were not modified by PR #49. They remain portfolio retirement/migration work and must be migrated and independently verified before claiming the entire GitHub portfolio is provider-independent.

## Verification boundary

PR #49 validates code and local D1 migration behavior only. It does not provision Cloudflare account resources, deploy production, restore deleted data, or prove that production products operate.

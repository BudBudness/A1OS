# Vercel and Supabase retirement — A1OS

## Target platform

A1OS is standardized on GitHub + Cloudflare + Termux. Vercel and Supabase are retired providers. No new integrations, deployments, credentials, cron jobs, or CI dependencies may be added.

## Removed from the A1OS core runtime

- Root Vercel deployment and cron configuration (vercel.json).
- Vercel-specific Python entrypoint configuration (pyproject.toml).
- Supabase task persistence client (core/persistence/supabase_tasks.py) and its provider-specific tests.
- Supabase/Vercel runtime selection in app.py.
- Supabase task polling/claiming/completion in core/worker.py; the worker now uses the shared durable queue facade backed by Cloudflare D1 or local SQLite.
- Supabase credentials from worker launch/status scripts and CI regression jobs.
- Vercel-specific config files under the Legal and Little Oaks verticals.
- Supabase credentials and provider-specific production smoke job from the Legal CI workflow.

## Remaining migration work — not yet retired

The repository still contains product-level Supabase integration code that must be migrated before it can be safely deleted:

- **Legal vertical:** Supabase JS SDK, browser client, authentication, database/RLS and associated historical migrations. Replace with an approved Cloudflare-backed data/auth design and verify confidentiality, authorization and tenant boundaries first.
- **YouTube High Profit:** optional Supabase job persistence and historical schema. Replace with Cloudflare D1/R2 or an explicitly approved local Termux persistence design, then verify job lifecycle and artifact recovery.
- **Historical supabase/ migration files:** retained as migration/audit evidence. They are not authorization to continue using Supabase.

## External decommissioning is separate

Repository changes do not uninstall GitHub Apps, delete Vercel projects/deployments, delete Supabase projects/databases, revoke provider credentials, or remove account-level integrations. Those operations require resource inventory, verified backups/restore, cutover evidence and explicit authorization. No external resource was changed by this PR.

## Verification gates

- CI must pass after the core runtime refactor.
- Confirm no active core imports or worker scripts depend on Supabase.
- Confirm no root or product Vercel deployment configuration remains.
- Complete Legal and YouTube High Profit migrations independently before deleting their remaining Supabase code or data.

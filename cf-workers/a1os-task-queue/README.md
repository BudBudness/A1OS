# A1OS D1 task queue Worker

A Cloudflare Worker API backed by a dedicated D1 database. It replaces the runtime dependency on a Supabase task store when the Python runtime is configured with A1OS_TASK_QUEUE_URL and A1OS_TASK_QUEUE_TOKEN.

## API

- GET /health — minimal public health response.
- POST /v1/tasks — enqueue an idempotent task.
- GET /v1/tasks/pending?limit=20 — list due queued/retry tasks.
- GET /v1/tasks/:id — read one task.
- POST /v1/tasks/:id/claim — atomic single-claim transition.
- POST /v1/tasks/:id/complete — complete only a running task.
- POST /v1/tasks/:id/fail — retry with bounded exponential delay, or fail terminally.
- POST /v1/tasks/recover — recover stale running leases.

All /v1 routes require Authorization: Bearer <TASK_QUEUE_TOKEN>. No browser CORS policy is enabled. Payloads are limited to 256 KiB. Task writes are restricted to authenticated callers; no public task execution or arbitrary worker dispatch is exposed.

## Local verification

Run npm install, npm run typecheck, and npm test in this directory. Run the D1 schema contract test with:

    python tests/validate_d1_task_queue.py

## Local D1 / Worker

Create a dedicated D1 database, replace the placeholder ID in wrangler.jsonc, then:

    npx wrangler d1 migrations apply a1os-task-queue --local
    npx wrangler dev --local

Set the secret with:

    npx wrangler secret put TASK_QUEUE_TOKEN

Do not deploy until the D1 database, secret, staging-only bindings, cost controls, and isolated deployment identity are independently verified. Production queue cutover is a separate release gate.

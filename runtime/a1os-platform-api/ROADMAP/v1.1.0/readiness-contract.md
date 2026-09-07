# A1OS Readiness Contract

GET /v1/health
- Liveness endpoint.
- Returns HTTP 200 while the process is alive.

GET /v1/ready
- Readiness endpoint.
- Verifies required application dependencies.
- Database must be reachable.
- Database integrity check must succeed.
- Returns HTTP 200 only when ready.
- Returns HTTP 503 when not ready.

GET /v1/readiness
- Compatibility alias for `/v1/ready`.

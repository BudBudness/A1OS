# INCIDENT RESPONSE

## Severity 1 — System unavailable
- Confirm API process.
- Confirm database availability.
- Check latest logs.
- Verify health endpoint.
- Roll back to last known-good commit if required.

## Severity 2 — Core workflow degraded
- Identify affected route.
- Preserve logs.
- Verify database integrity.
- Apply targeted fix.
- Run relevant acceptance tests.

## Severity 3 — Non-critical defect
- Record incident.
- Create corrective task.
- Schedule fix.
- Verify through acceptance testing.

## Rollback
1. Stop current API.
2. Restore last known-good Git commit.
3. Restore database backup if required.
4. Start API.
5. Verify health.
6. Verify authentication.
7. Run acceptance suite.

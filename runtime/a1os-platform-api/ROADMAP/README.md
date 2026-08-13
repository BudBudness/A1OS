# A1OS Platform API — Roadmap

## v1.0 (delivered)
- Multi-tenant FastAPI backend with org-scoped resources
- SSO-style auth (opaque tokens, PBKDF2 hashing, rate-limited login)
- Organizations, users, roles with custom permission sets
- Parties (customers/suppliers/farmers/buyers), products catalog
- Double-entry ledger with balances + trial balance
- Inventory / warehouse with movements and on-hand quantities
- Notifications queue, audit log
- Realtime WebSocket channel per organization

## Next
- Integration tokens / machine-to-machine auth for frontends
- Files / documents
- Webhook dispatch for notifications
- Export APIs (CSV/Excel)
- Pluggable industry modules (coffee, school, charity)

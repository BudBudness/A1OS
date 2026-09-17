# A1OS Invariants

1. One authoritative production API.
2. One authoritative production database.
3. One supervisor owns each managed service.
4. No duplicate daemons.
5. No hidden autonomous execution.
6. No unrestricted AI shell execution.
7. Every consequential action has an authority decision.
8. Every execution has verification.
9. Every consequential execution has an audit record.
10. Database migrations are versioned and validated.
11. Secrets are never printed into logs or UI.
12. Storage cleanup is policy-driven and must protect production data.
13. Releases require evidence.
14. Failed release validation stops promotion.
15. Organization data is tenant-scoped.
16. Product customization is configuration-driven, not fork-driven.
17. Existing production functionality is preserved unless explicitly replaced.
18. Legacy components are not revived merely because they exist on disk.

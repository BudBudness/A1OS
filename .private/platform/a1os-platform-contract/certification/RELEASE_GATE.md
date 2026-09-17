# Production Release Gate

A release must pass:

1. syntax/static validation
2. compilation
3. tests
4. database/migration validation
5. backup verification
6. service startup
7. local health
8. local readiness
9. API endpoint verification
10. public endpoint verification where applicable
11. process/service uniqueness check
12. storage safety check
13. audit evidence

Any failed gate blocks release.

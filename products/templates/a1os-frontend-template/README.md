# A1OS Frontend Vertical Template

Canonical template for A1OS frontend-only verticals.

## Structure

- pages/
- components/
- layouts/
- dashboards/
- workflows/
- forms/
- state/
- integrations/
- styles/
- assets/
- tests/

## Rules

1. A vertical is frontend-first.
2. Vertical-specific databases are not owned here.
3. Vertical-specific backend servers are not owned here.
4. Vertical-specific deployment infrastructure is not owned here.
5. Authentication, tenancy and authorization use A1OS platform contracts.
6. External systems are accessed through integration contracts.
7. Business data remains in the customer's existing system unless explicitly provided by the platform.

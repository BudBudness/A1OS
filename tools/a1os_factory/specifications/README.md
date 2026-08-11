# A1OS Vertical Specification

The vertical specification is the factory input contract.

## Ownership

- UI: generated vertical
- Pages: generated vertical
- Components: generated vertical
- Workflows: generated vertical
- Assets: generated vertical
- Deployment configuration: generated vertical
- Domain data: A1OS Platform API
- Authentication: A1OS Core
- Tenancy: A1OS Core
- Authorization: A1OS Core
- RBAC: A1OS Core

A vertical specification MUST NOT define:

- a database
- database credentials
- backend services
- backend routes
- a dedicated authentication system
- a dedicated tenancy system
- a dedicated RBAC system
- infrastructure ownership

The specification describes WHAT the frontend needs. A1OS decides HOW the shared platform supplies it.

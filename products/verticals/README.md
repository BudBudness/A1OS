# A1OS Frontend Verticals

This directory contains frontend-only A1OS verticals.

## Contract

Each vertical may contain:

- pages
- components
- layouts
- dashboards
- workflows
- forms
- frontend state
- integrations
- styles
- assets
- tests

A vertical must NOT own:

- a dedicated database
- a dedicated backend server
- a dedicated deployment platform
- a dedicated watchdog
- a dedicated infrastructure stack

Shared authentication, tenancy, authorization, RBAC and integrations belong to A1OS Core/Platform.

Existing backend systems may remain elsewhere during migration but are not part of the frontend vertical contract.

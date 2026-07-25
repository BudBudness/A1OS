# STAFF & HR MODULE

## Objective

Upgrade the existing users/RBAC foundation into a production-grade Staff & HR operational module.

## Current Foundation

- users table exists
- Authentication exists
- RBAC exists
- Role permissions exist
- GET /staff exists
- Operations can assign tasks to staff
- Current authenticated user is available through auth context

## Required Capability

### Staff Directory

- List all staff
- View staff profile
- Filter active/inactive staff
- Filter by role
- Search by name, email, or phone

### Staff Profiles

- Full name
- Role
- Email
- Phone
- Active status
- Organization
- Created date

### Staff Lifecycle

- Create staff account
- Update staff profile
- Activate staff
- Deactivate staff
- Change role
- Reset password

### Roles

Existing roles:

- director_ceo_teacher
- head_mistress
- staff

All role changes must respect RBAC authorization.

### Operational Integration

Staff must integrate with:

- School operations assignment
- Attendance recording
- Audit log
- Authentication
- Intelligence summary

### Audit Requirements

Record:

- staff_created
- staff_updated
- staff_activated
- staff_deactivated
- staff_role_changed
- staff_password_reset

### Security Requirements

- Passwords must never be returned by API
- Inactive staff cannot authenticate
- Role changes must be audited
- Only authorized users may manage staff
- Staff may view only what their permissions allow

## API Contract

Required endpoints:

GET    /staff
GET    /staff/{staff_id}
POST   /staff
PATCH  /staff/{staff_id}
PATCH  /staff/{staff_id}/status
PATCH  /staff/{staff_id}/role
POST   /staff/{staff_id}/reset-password

## Frontend Contract

Create a dedicated Staff & HR interface.

Required views:

- Staff directory
- Staff profile
- Role/status filters
- Staff creation form
- Edit staff form
- Activate/deactivate action
- Role management action

## Acceptance Criteria

- Existing authentication remains operational
- Existing RBAC remains operational
- Existing staff records remain intact
- Existing operations assignment remains operational
- New staff endpoints require authentication
- Unauthorized role changes are rejected
- Inactive staff cannot log in
- All lifecycle changes appear in audit_log
- Frontend and API contracts pass
- Production release audit remains PASS

## Definition of Done

STAFF / HR: OPERATIONAL
AUTHENTICATION: PASS
RBAC: PASS
AUDIT TRAIL: PASS
OPERATIONS INTEGRATION: PASS
FRONTEND: PASS
FINAL DELIVERY: PASS

# Staff / HR Frontend Surface

## Objective
Create a dedicated premium Staff / HR management interface for Little Oaks Education OS.

## Required Capabilities
- View active staff
- Search staff
- Filter by role
- View staff profile
- Create staff account
- Edit staff profile
- Activate/deactivate staff
- Change staff role
- Reset staff password
- Display permission-aware actions
- Preserve same-origin API architecture
- Preserve authoritative CSS design system

## API Contract
- GET /staff
- GET /staff/{staff_id}
- POST /staff
- PATCH /staff/{staff_id}
- PATCH /staff/{staff_id}/status
- PATCH /staff/{staff_id}/role
- POST /staff/{staff_id}/reset-password

## Security
- Authentication required
- Permission-aware controls
- No password hashes exposed
- No plaintext passwords persisted
- Organization-scoped records
- Audit all administrative mutations

## UX
- Dedicated Staff / HR navigation surface
- Executive summary header
- Staff directory
- Role/status badges
- Profile drawer or detail panel
- Confirmation for destructive actions
- Loading, empty, and error states
- Mobile-responsive layout

## Acceptance Criteria
- No unfinished/debug references
- No duplicate design tokens
- No new frontend framework
- No cross-origin API calls
- All API mutations authenticated
- Static asset delivery remains same-origin
- Existing production audit remains PASS

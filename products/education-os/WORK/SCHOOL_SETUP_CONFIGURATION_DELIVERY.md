# LITTLE OAKS EDUCATION OS — SCHOOL SETUP / CONFIGURATION DELIVERY

Generated: 2026-07-24T21:36:39.142250+00:00

## OBJECTIVE

Build the real school configuration workflow for Little Oaks Montessori Nursery & Kindergarten.

## LETICIA MUST BE ABLE TO CONFIGURE

### Academic structure
- Academic year
- Academic periods / terms
- Start dates
- End dates
- Active period

### Classes
- Class name
- Class level
- Capacity
- Active/inactive state

### Fee structure
- Fee type
- Amount
- Academic period
- Class level
- Due date
- Active/inactive state

## REQUIRED WORKFLOW

School Setup
  -> Create academic year
  -> Create term
  -> Create class levels
  -> Configure fees
  -> Enroll students
  -> Generate fee obligations

## REQUIRED UI

Add a School Setup / Configuration workflow accessible to authorized users.

Sections:

1. Academic Years
2. Academic Periods
3. Class Levels
4. Fee Structures

The UI must use the existing authoritative Little Oaks visual system and remain responsive on desktop and mobile.

## REQUIRED DATA MODEL

Use the existing organization_id tenancy model.

Do not create synthetic students, synthetic payments, acceptance records, or test fee obligations in the active production database.

All configuration mutations must be auditable.

## REQUIRED BUSINESS RULES

- Only authorized staff can modify configuration.
- A school may have one active academic year.
- An academic period belongs to an academic year.
- A fee structure belongs to an academic period.
- A student fee obligation must be generated from an actual configured fee structure.
- Fee structures must not silently modify historical obligations.
- Historical payments and obligations remain immutable except through explicit authorized correction workflows.

## DELIVERY ORDER

1. Inspect actual current schema.
2. Create a safety backup.
3. Add only missing configuration tables required by the workflow.
4. Add API contracts.
5. Add frontend UI.
6. Add authorization checks.
7. Add audit logging.
8. Add mobile-responsive behavior.
9. Run Python syntax verification.
10. Run JavaScript syntax verification.
11. Run acceptance verification.
12. Run final release audit.
13. Verify production service on port 3012.
14. Verify same-origin asset delivery.
15. Verify authentication.
16. Verify configuration API contracts.
17. Verify database integrity.

## RELEASE CONDITION

Do not report delivery as complete unless:

- School Setup UI loads.
- Academic year can be created.
- Academic period can be created.
- Class level can be created.
- Fee structure can be created.
- Configuration is organization-scoped.
- Existing real workflows continue to work.
- No acceptance/test data is inserted into the active database.
- Final audit passes with no unfinished-work warnings.

## IMPORTANT

The existing active database was previously contaminated by acceptance data including:

- Frontend Integration-c8f7507e
- rbac_test fee
- Production Acceptance Verification
- Final Acceptance sessions

Do not use those records as production examples.

The next implementation must use the actual current files and actual schema rather than assuming a schema.


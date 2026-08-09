# Little Oaks Education OS — Academic Operations

## Objective

Operationalise the existing academic data model into a complete school-management workflow.

## Existing academic entities

- academic_years
- academic_periods
- class_levels
- students
- admissions

## Academic Operations scope

### 1. Academic Years
- Create academic year
- Set active academic year
- Prevent conflicting active periods
- Archive completed years

### 2. Academic Periods
- Term / semester management
- Start and end dates
- Status tracking
- Current-period resolution

### 3. Class Levels
- Nursery and kindergarten class structure
- Class level activation
- Ordering and display sequence

### 4. Student Academic Placement
- Assign active students to class levels
- Track academic year
- Track academic period
- Prevent duplicate active placement

### 5. Teacher Assignment
- Assign staff to class levels
- Validate staff identity and active status
- Track assignment period

### 6. Academic Calendar
- School opening and closing dates
- Term boundaries
- Operational date awareness

## Implementation sequence

1. Schema inventory
2. API contract
3. Authentication and RBAC
4. Backend implementation
5. Authenticated E2E acceptance
6. Frontend management surface
7. Frontend integration audit
8. Full module acceptance
9. Release audit
10. Commit and push

## Completion standard

Academic Operations is complete only when:

- API contracts pass
- Organization isolation passes
- Authentication passes
- RBAC passes
- Academic year lifecycle passes
- Academic period lifecycle passes
- Class-level management passes
- Student placement passes
- Teacher assignment passes
- Frontend integration passes
- JavaScript and Python syntax pass
- Authenticated E2E acceptance passes
- Production release audit passes
- GitHub main branch is clean and synchronized

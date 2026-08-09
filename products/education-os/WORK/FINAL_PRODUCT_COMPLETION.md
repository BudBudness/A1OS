# LITTLE OAKS EDUCATION OS — FINAL PRODUCT COMPLETION

Turn every existing API contract into a complete, real-world Little Oaks Montessori Nursery & Kindergarten workflow.

PRIORITY ORDER:

1. CLEAN ACTIVE DATABASE
2. COMPLETE FEES & PAYMENTS
3. COMPLETE ATTENDANCE
4. COMPLETE SCHOOL OPERATIONS
5. UPGRADE DASHBOARD INTO SCHOOL INTELLIGENCE
6. REFINE DESKTOP/MOBILE BEHAVIOUR
7. RUN COMPLETE RELEASE VALIDATION

NON-NEGOTIABLE:
- Preserve the existing premium Little Oaks visual design system.
- Preserve the authoritative CSS design tokens.
- Preserve authentication and authorization.
- Preserve same-origin delivery.
- Do not invent new backend APIs where existing API contracts are sufficient.
- Do not leave fake UI such as "data loaded".
- Do not leave unfinished workflow buttons.
- Do not add test data to the active database.
- Do not break existing API contracts.
- All Python and JavaScript must remain syntactically valid.

============================================================
1. CLEAN ACTIVE DATABASE
============================================================

Create a backup before mutation.

Remove only known acceptance/test records identifiable by:
- Frontend Integration-c8f7507e
- Verification Student
- Final Acceptance 1784921662
- Final Acceptance 223202
- Final Acceptance 223203
- Production Acceptance Verification

Do not delete legitimate Little Oaks institutional data.

Verify database counts after cleanup.

============================================================
2. COMPLETE FEES & PAYMENTS
============================================================

Use the existing API contracts:

GET /fees
GET /fees/{fee_id}
POST /fees
PATCH /fees/{fee_id}
GET /payments
GET /payments/{payment_id}
POST /payments

Implement a real school financial workflow:

- fee obligations by student
- student/account context
- amount due
- amount paid
- outstanding balance
- payment history
- record payment
- payment status
- payment date
- payment method where supported
- reference/receipt information where supported
- financial summary metrics
- loading states
- error states
- legitimate empty states
- responsive desktop and mobile presentation

Do not fabricate financial data.

============================================================
3. COMPLETE ATTENDANCE
============================================================

Use:

POST /attendance/sessions
POST /attendance/sessions/{session_id}/records
GET /attendance/sessions
GET /attendance/sessions/{session_id}

Implement:

- attendance date
- class
- create attendance session
- student roster
- Present
- Absent
- Late
- Excused only if supported by the existing schema
- save attendance records
- session detail view
- attendance totals
- attendance summary
- duplicate handling
- loading states
- error states
- legitimate empty states

============================================================
4. COMPLETE SCHOOL OPERATIONS
============================================================

Use:

POST /operations
GET /operations
GET /operations/{operation_id}
PATCH /operations/{operation_id}/status

Implement:

- operations list
- create operation
- title
- category where supported
- description
- priority where supported
- status
- responsible person where supported
- due date where supported
- operation detail view
- status updates
- operational summary
- loading states
- error states
- legitimate empty states

Remove fake output such as:
"Operations data loaded."

============================================================
5. UPGRADE DASHBOARD
============================================================

Replace static counters with actual school intelligence derived from available API data.

Use available data to show:

- total students
- active admissions
- financial position where derivable
- outstanding fees where derivable
- attendance overview where derivable
- recent admissions
- recent payments
- attendance overview
- operational items requiring attention
- actionable quick actions

Do not invent metrics that cannot be derived from available data.

============================================================
6. INSTITUTIONAL IDENTITY
============================================================

Brand hierarchy:

Primary brand:
Little Oaks

Full institution:
Little Oaks Montessori Nursery & Kindergarten

Platform:
Little Oaks Education OS

Use the full institutional name where institutional context requires it while retaining the premium Little Oaks brand presentation.

============================================================
7. DESKTOP / MOBILE
============================================================

After the workflows are complete:

- verify desktop usability
- verify mobile usability
- ensure tables remain usable on small screens
- ensure forms remain usable
- ensure navigation remains usable
- preserve premium design tokens
- preserve current visual identity
- refine layout based on real workflows rather than generic responsive changes

============================================================
8. FINAL VALIDATION
============================================================

Run:

- Python syntax checks
- JavaScript syntax checks for every frontend JavaScript file
- unfinished work audit
- placeholder audit
- frontend reference audit
- CSS token/design-system audit
- DOM/CSS correspondence audit
- API health
- same-origin asset delivery
- authentication
- core data contracts
- process/port validation

Final report must clearly show PASS or FAIL.

No hidden warnings.

Do not stop after changing files.
Implement the workflows, validate them, and report the final release status.

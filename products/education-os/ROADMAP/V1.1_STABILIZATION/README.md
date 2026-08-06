# Version 1.1 — Stabilization

## Delivered (v1.1.0)

### Reporting improvements
- `/reports` adds `attendance.rate` (present %) and `fees.collection_rate` (paid/billed %) — `null` when no data, no divide-by-zero.
- Removed duplicate `academic_periods` query that re-counted `academic_terms`; academic counts now computed once.

### Data quality
- Duplicate `admission_number` now returns **409** with a clear message instead of an unhandled `IntegrityError` → 500. The `students.admission_number` UNIQUE constraint is enforced gracefully.

### Performance / usability — pagination + search
- Backward-compatible `limit` / `offset` on list endpoints: `/students`, `/parents`, `/fees`, `/payments`, `/operations`, `/attendance`, `/admissions`, `/audit`.
- `search` filter on `/students` (name/admission), `/parents` (name/phone/email), `/fees` (type/status/student), `/payments` (reference/method/status), `/audit` (entity/action/actor).
- `/attendance` gains a `status` filter.
- Responses that already returned `{"count": ...}` now report the total matching `count` across pages (not just the page length).

### Staff workflow
- `PATCH /students/{id}` — edit name, DOB, gender, class level, enrollment status, guardian details (422 when no editable fields, 404 when missing).
- `PATCH /students/{id}/status` — enrollment status transitions constrained to `active | inactive | graduated | transferred | withdrawn`.

### Acceptance
- New suite: `WORK/V1_1_STABILIZATION/LIVE_ACCEPTANCE/v1_1_acceptance.py` (18 checks).
- Stages 4–7 acceptance suites all pass against the live stack with the changes.

## Outstanding priorities (hypercare-driven)
- Production defects surfaced in hypercare
- Usability friction
- Performance bottlenecks
- Reporting improvements
- Data quality issues
- Staff workflow improvements
- Backup and recovery improvements

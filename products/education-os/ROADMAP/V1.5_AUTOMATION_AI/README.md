# Version 1.5 — Automation and Intelligence

## Delivered (v1.5.0)

### Fee arrears intelligence
- `GET /intelligence/fee-arrears` — totals outstanding, students in arrears, and a full arrears list (student, fee type, period, amount, paid, outstanding, due date, guardian contact), sorted by arrears descending.

### Director daily briefing
- `GET /intelligence/briefing` — dated daily digest: KPIs (students, attendance rate, collection rate, outstanding, arrears, pending admissions, open operations), top-5 arrears, prioritized insights, and alert summary. Replaces the previously hardcoded zero/empty intelligence summary values with live data.

### Automated fee reminders
- `GET /intelligence/fee-reminders` — generates dispatch-ready reminder records for obligations past due with an outstanding balance: student + guardian contact, amount owed, days overdue, and suggested channel (`sms` when a guardian phone is on file).

### Acceptance
- New suite: `WORK/V1_5_AUTOMATION_AI/LIVE_ACCEPTANCE/v1_5_acceptance.py` (11 checks) — creates a real overdue obligation end-to-end, verifies all three surfaces reflect it, then cleans up (no residue).
- Stages 4–7, V1.1, and V1.5 suites all pass (127 checks) against the live stack.

## Candidate capabilities (next)
- Parent communication workflows
- Attendance alerts
- Automated report generation
- Risk detection
- Student performance trends
- Staff activity intelligence

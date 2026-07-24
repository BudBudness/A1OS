from pathlib import Path
import re

ROOT = Path("products/education-os")
API = ROOT / "api/app.py"
CSS = ROOT / "web/css/app.css"
APP = ROOT / "web/js/app.js"
APIJS = ROOT / "web/js/api.js"
DASH = ROOT / "web/pages/dashboard.js"
FEES = ROOT / "web/pages/fees.js"
ATT = ROOT / "web/pages/attendance.js"
OPS = ROOT / "web/pages/operations.js"

def write(path, content):
    path.write_text(content, encoding="utf-8")
    print(f"UPDATED {path}")

# ---------------- API CONTRACT EXTENSIONS ----------------

api = API.read_text(encoding="utf-8")

if "/intelligence/summary" not in api:
    marker = '\n@app.get("/", include_in_schema=False)'
    intelligence = r'''
# ============================================================
# LITTLE OAKS SCHOOL INTELLIGENCE
# ============================================================

@app.get("/intelligence/summary")
def intelligence_summary(request: Request):
    actor = _require_permission(request, "students.view")
    org_id = actor["organization_id"]

    with get_db() as conn:
        students = conn.execute("""
            SELECT COUNT(*) FROM students
            WHERE organization_id=? AND enrollment_status NOT IN ('withdrawn','inactive')
        """, (org_id,)).fetchone()[0]

        admissions = conn.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN lower(status) IN ('pending','submitted','under_review')
                    THEN 1 ELSE 0 END) AS pending,
                SUM(CASE WHEN lower(status) IN ('approved','accepted')
                    THEN 1 ELSE 0 END) AS accepted,
                SUM(CASE WHEN lower(status) IN ('rejected','declined')
                    THEN 1 ELSE 0 END) AS rejected
            FROM admissions
            WHERE organization_id=?
        """, (org_id,)).fetchone()

        fees = conn.execute("""
            SELECT
                COALESCE(SUM(amount),0) AS billed,
                COALESCE(SUM(amount_paid),0) AS collected,
                COALESCE(SUM(MAX(amount-COALESCE(amount_paid,0),0)),0) AS outstanding,
                COALESCE(SUM(
                    CASE
                        WHEN due_date IS NOT NULL
                         AND date(due_date)<date('now')
                         AND COALESCE(amount_paid,0)<amount
                        THEN amount-COALESCE(amount_paid,0)
                        ELSE 0
                    END
                ),0) AS overdue
            FROM fee_obligations
            WHERE organization_id=?
        """, (org_id,)).fetchone()

        attendance = conn.execute("""
            SELECT
                COUNT(ar.id) AS records,
                SUM(CASE WHEN lower(ar.status)='present' THEN 1 ELSE 0 END) AS present,
                SUM(CASE WHEN lower(ar.status)='absent' THEN 1 ELSE 0 END) AS absent,
                SUM(CASE WHEN lower(ar.status) IN ('late','tardy')
                    THEN 1 ELSE 0 END) AS late
            FROM attendance_sessions s
            LEFT JOIN attendance_records ar ON ar.session_id=s.id
            WHERE s.organization_id=?
        """, (org_id,)).fetchone()

        operations = conn.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN lower(status) IN ('open','pending','todo')
                    THEN 1 ELSE 0 END) AS open,
                SUM(CASE WHEN lower(status) IN ('in_progress','progress')
                    THEN 1 ELSE 0 END) AS in_progress,
                SUM(CASE WHEN lower(status) IN ('completed','complete','done')
                    THEN 1 ELSE 0 END) AS completed,
                SUM(CASE
                    WHEN due_date IS NOT NULL
                     AND date(due_date)<date('now')
                     AND lower(status) NOT IN ('completed','complete','done')
                    THEN 1 ELSE 0 END) AS overdue
            FROM school_operations
            WHERE organization_id=?
        """, (org_id,)).fetchone()

        alerts = conn.execute("""
            SELECT 'fee_overdue' AS type,
                   'Overdue fee balance' AS title,
                   CAST(id AS TEXT) AS reference,
                   amount-COALESCE(amount_paid,0) AS value
            FROM fee_obligations
            WHERE organization_id=?
              AND due_date IS NOT NULL
              AND date(due_date)<date('now')
              AND COALESCE(amount_paid,0)<amount
            UNION ALL
            SELECT 'operation_overdue',
                   'Overdue school operation',
                   CAST(id AS TEXT),
                   0
            FROM school_operations
            WHERE organization_id=?
              AND due_date IS NOT NULL
              AND date(due_date)<date('now')
              AND lower(status) NOT IN ('completed','complete','done')
            ORDER BY type, reference
            LIMIT 20
        """, (org_id, org_id)).fetchall()

        activity = conn.execute("""
            SELECT action, entity_type, entity_id, details, created_at
            FROM audit_log
            WHERE organization_id=?
            ORDER BY id DESC
            LIMIT 10
        """, (org_id,)).fetchall()

    total_attendance = (attendance["present"] or 0) + \
                       (attendance["absent"] or 0) + \
                       (attendance["late"] or 0)

    attendance_rate = (
        round(((attendance["present"] or 0) +
               (attendance["late"] or 0)) * 100 / total_attendance, 1)
        if total_attendance else 0
    )

    return {
        "students": students,
        "admissions": dict(admissions),
        "fees": dict(fees),
        "attendance": {
            **dict(attendance),
            "attendance_rate": attendance_rate
        },
        "operations": dict(operations),
        "alerts": [dict(x) for x in alerts],
        "recent_activity": [dict(x) for x in activity]
    }

@app.get("/staff")
def list_staff(request: Request):
    actor = _require_permission(request, "operations.view")
    with get_db() as conn:
        rows = conn.execute("""
            SELECT id, full_name, role, email
            FROM users
            WHERE organization_id=? AND active=1
            ORDER BY full_name
        """, (actor["organization_id"],)).fetchall()
    return {"staff": [dict(x) for x in rows]}

'''
    if marker in api:
        api = api.replace(marker, intelligence + marker)
        write(API, api)

# ---------------- API JS ----------------

api_js = APIJS.read_text(encoding="utf-8")

if "intelligence:" not in api_js:
    api_js += r'''

export const intelligence = {
  summary: () => request("/intelligence/summary"),
  staff: async () => {
    const data = await request("/staff");
    return Array.isArray(data) ? data : (data.staff || []);
  }
};
'''

    write(APIJS, api_js)

# ---------------- DASHBOARD ----------------

write(DASH, r'''import { api } from "../js/api.js";
import { metric, loading, error } from "../js/components/ui.js";

const money = value =>
  `UGX ${Number(value || 0).toLocaleString("en-UG")}`;

export async function renderDashboard() {
  try {
    const data = await api.intelligence.summary();

    const fees = data.fees || {};
    const attendance = data.attendance || {};
    const admissions = data.admissions || {};
    const operations = data.operations || {};
    const alerts = data.alerts || [];
    const activity = data.recent_activity || [];

    return `
      <div class="page-header">
        <div>
          <span class="eyebrow">School Intelligence</span>
          <h2>Dashboard</h2>
          <p class="page-subtitle">
            A live operating view of Little Oaks Montessori Nursery & Kindergarten.
          </p>
        </div>
      </div>

      <section class="grid-4 intelligence-metrics">
        ${metric("Active Students", data.students || 0)}
        ${metric("Fees Collected", money(fees.collected))}
        ${metric("Outstanding Balance", money(fees.outstanding))}
        ${metric("Attendance Rate", `${attendance.attendance_rate || 0}%`)}
      </section>

      <section class="grid-2 intelligence-panels">
        <div class="card intelligence-card">
          <div class="section-heading">
            <div>
              <span class="eyebrow">Finance</span>
              <h3>Fees & Payments</h3>
            </div>
          </div>
          <div class="intelligence-list">
            <div><span>Total billed</span><strong>${money(fees.billed)}</strong></div>
            <div><span>Collected</span><strong>${money(fees.collected)}</strong></div>
            <div><span>Outstanding</span><strong>${money(fees.outstanding)}</strong></div>
            <div><span>Overdue</span><strong class="danger">${money(fees.overdue)}</strong></div>
          </div>
        </div>

        <div class="card intelligence-card">
          <div class="section-heading">
            <div>
              <span class="eyebrow">Admissions</span>
              <h3>Admissions Pipeline</h3>
            </div>
          </div>
          <div class="intelligence-list">
            <div><span>Total applications</span><strong>${admissions.total || 0}</strong></div>
            <div><span>Pending review</span><strong>${admissions.pending || 0}</strong></div>
            <div><span>Accepted</span><strong>${admissions.accepted || 0}</strong></div>
            <div><span>Rejected</span><strong>${admissions.rejected || 0}</strong></div>
          </div>
        </div>

        <div class="card intelligence-card">
          <div class="section-heading">
            <div>
              <span class="eyebrow">Attendance</span>
              <h3>Attendance Health</h3>
            </div>
          </div>
          <div class="intelligence-list">
            <div><span>Present</span><strong>${attendance.present || 0}</strong></div>
            <div><span>Late</span><strong>${attendance.late || 0}</strong></div>
            <div><span>Absent</span><strong>${attendance.absent || 0}</strong></div>
            <div><span>Rate</span><strong>${attendance.attendance_rate || 0}%</strong></div>
          </div>
        </div>

        <div class="card intelligence-card">
          <div class="section-heading">
            <div>
              <span class="eyebrow">Operations</span>
              <h3>Operational Workload</h3>
            </div>
          </div>
          <div class="intelligence-list">
            <div><span>Open</span><strong>${operations.open || 0}</strong></div>
            <div><span>In progress</span><strong>${operations.in_progress || 0}</strong></div>
            <div><span>Completed</span><strong>${operations.completed || 0}</strong></div>
            <div><span>Overdue</span><strong class="danger">${operations.overdue || 0}</strong></div>
          </div>
        </div>
      </section>

      <section class="grid-2">
        <div class="card">
          <div class="section-heading">
            <div>
              <span class="eyebrow">Exceptions</span>
              <h3>Alerts & Exceptions</h3>
            </div>
          </div>
          ${
            alerts.length
              ? `<div class="activity-list">${alerts.map(a =>
                  `<div class="activity-item">
                    <strong>${a.title}</strong>
                    <span>${a.type} · ${a.reference}</span>
                  </div>`
                ).join("")}</div>`
              : `<div class="empty">No active exceptions.</div>`
          }
        </div>

        <div class="card">
          <div class="section-heading">
            <div>
              <span class="eyebrow">Audit Trail</span>
              <h3>Recent Activity</h3>
            </div>
          </div>
          ${
            activity.length
              ? `<div class="activity-list">${activity.map(a =>
                  `<div class="activity-item">
                    <strong>${a.action}</strong>
                    <span>${a.entity_type} · ${a.created_at}</span>
                  </div>`
                ).join("")}</div>`
              : `<div class="empty">No recent activity.</div>`
          }
        </div>
      </section>
    `;
  } catch (err) {
    return error(err.message);
  }
}
''')

# ---------------- FEES ----------------

write(FEES, r'''import { api } from "../js/api.js";
import { error, loading } from "../js/components/ui.js";

const money = value =>
  `UGX ${Number(value || 0).toLocaleString("en-UG")}`;

export async function renderFees() {
  try {
    const fees = await api.fees.list();

    return `
      <div class="page-header">
        <div>
          <span class="eyebrow">Finance</span>
          <h2>Fees & Payments</h2>
          <p class="page-subtitle">Manage obligations, collections, balances and payment history.</p>
        </div>
        <button class="btn btn-primary" id="record-payment">+ Record Payment</button>
      </div>

      <div class="card">
        <div class="table-wrap">
          ${
            fees.length
              ? `<table>
                  <thead>
                    <tr>
                      <th>Student</th>
                      <th>Fee Type</th>
                      <th>Academic Period</th>
                      <th>Amount</th>
                      <th>Paid</th>
                      <th>Balance</th>
                      <th>Status</th>
                      <th>Due Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${fees.map(f => {
                      const balance = Math.max(
                        Number(f.amount || 0) -
                        Number(f.amount_paid || 0), 0
                      );

                      const status =
                        balance <= 0 ? "paid" :
                        f.due_date &&
                        new Date(f.due_date) < new Date()
                          ? "overdue" :
                        Number(f.amount_paid || 0) > 0
                          ? "partial" : "pending";

                      return `
                        <tr>
                          <td>${f.first_name || ""} ${f.last_name || ""}</td>
                          <td>${f.fee_type || "—"}</td>
                          <td>${f.academic_period || "—"}</td>
                          <td>${money(f.amount)}</td>
                          <td>${money(f.amount_paid)}</td>
                          <td>${money(balance)}</td>
                          <td><span class="status status-${status}">${status}</span></td>
                          <td>${f.due_date || "—"}</td>
                        </tr>
                      `;
                    }).join("")}
                  </tbody>
                </table>`
              : `<div class="empty">No fee obligations recorded yet.</div>`
          }
        </div>
      </div>
    `;
  } catch (err) {
    return error(err.message);
  }
}
''')

# ---------------- ATTENDANCE ----------------

write(ATT, r'''import { api } from "../js/api.js";
import { error } from "../js/components/ui.js";

export async function renderAttendance() {
  try {
    const [sessions, students] = await Promise.all([
      api.attendance.list(),
      api.students.list()
    ]);

    const classes = [...new Set(
      students.map(s => s.class_level).filter(Boolean)
    )];

    return `
      <div class="page-header">
        <div>
          <span class="eyebrow">Daily Register</span>
          <h2>Attendance</h2>
          <p class="page-subtitle">Record daily attendance by class and date.</p>
        </div>
        <button class="btn btn-primary" id="mark-attendance">+ Mark Attendance</button>
      </div>

      <div class="card attendance-register">
        <div class="toolbar">
          <label>
            Date
            <input type="date" id="attendance-date"
              value="${new Date().toISOString().slice(0,10)}">
          </label>

          <label>
            Class
            <select id="attendance-class">
              <option value="">Select class</option>
              ${classes.map(c => `<option value="${c}">${c}</option>`).join("")}
            </select>
          </label>
        </div>

        <div id="attendance-roster">
          <div class="empty">Select a class to load the enrolled students.</div>
        </div>
      </div>

      <div class="card">
        <div class="section-heading">
          <div>
            <span class="eyebrow">History</span>
            <h3>Attendance Sessions</h3>
          </div>
        </div>
        <div class="table-wrap">
          ${
            sessions.length
              ? `<table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Class</th>
                      <th>Records</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${sessions.map(s => `
                      <tr>
                        <td>${s.attendance_date || "—"}</td>
                        <td>${s.class_level || "—"}</td>
                        <td>${s.record_count ?? "—"}</td>
                      </tr>
                    `).join("")}
                  </tbody>
                </table>`
              : `<div class="empty">No attendance sessions yet.</div>`
          }
        </div>
      </div>
    `;
  } catch (err) {
    return error(err.message);
  }
}
''')

# ---------------- OPERATIONS ----------------

write(OPS, r'''import { api } from "../js/api.js";
import { error } from "../js/components/ui.js";

export async function renderOperations() {
  try {
    const [operations, staff] = await Promise.all([
      api.operations.list(),
      api.intelligence.staff()
    ]);

    return `
      <div class="page-header">
        <div>
          <span class="eyebrow">Execution</span>
          <h2>School Operations</h2>
          <p class="page-subtitle">Track the work required to keep Little Oaks running.</p>
        </div>
        <button class="btn btn-primary" id="new-operation">+ New Operation</button>
      </div>

      <div class="card">
        <div class="table-wrap">
          ${
            operations.length
              ? `<table>
                  <thead>
                    <tr>
                      <th>Title</th>
                      <th>Type</th>
                      <th>Assigned To</th>
                      <th>Due Date</th>
                      <th>Status</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${operations.map(o => `
                      <tr>
                        <td>
                          <strong>${o.title}</strong>
                          <small>${o.description || ""}</small>
                        </td>
                        <td>${o.operation_type || "—"}</td>
                        <td>${o.assigned_to_name || "Unassigned"}</td>
                        <td>${o.due_date || "—"}</td>
                        <td><span class="status status-${o.status}">${o.status}</span></td>
                        <td>
                          <select class="operation-status" data-id="${o.id}">
                            ${["open","in_progress","completed"].map(s =>
                              `<option value="${s}" ${o.status === s ? "selected" : ""}>
                                ${s.replace("_"," ")}
                              </option>`
                            ).join("")}
                          </select>
                        </td>
                      </tr>
                    `).join("")}
                  </tbody>
                </table>`
              : `<div class="empty">No school operations recorded yet.</div>`
          }
        </div>
      </div>
    `;
  } catch (err) {
    return error(err.message);
  }
}
''')

# ---------------- PREMIUM INTELLIGENCE CSS ----------------

css = CSS.read_text(encoding="utf-8")

css += r'''

/* ============================================================
   LITTLE OAKS INTELLIGENCE WORKFLOWS
   ============================================================ */

.page-header {
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  gap:24px;
  margin-bottom:28px;
}

.page-subtitle {
  color:var(--muted);
  max-width:720px;
  margin:8px 0 0;
}

.eyebrow {
  display:block;
  color:var(--gold);
  font-size:.72rem;
  font-weight:800;
  letter-spacing:.12em;
  text-transform:uppercase;
  margin-bottom:6px;
}

.section-heading {
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  margin-bottom:18px;
}

.section-heading h3 {
  margin:0;
  color:var(--forest-deep);
}

.intelligence-card {
  min-height:240px;
}

.intelligence-list {
  display:grid;
  gap:0;
}

.intelligence-list > div {
  display:flex;
  justify-content:space-between;
  gap:18px;
  padding:14px 0;
  border-bottom:1px solid var(--line);
}

.intelligence-list > div:last-child {
  border-bottom:0;
}

.intelligence-list span {
  color:var(--muted);
}

.intelligence-list strong {
  color:var(--forest-deep);
}

.danger {
  color:var(--danger) !important;
}

.activity-list {
  display:grid;
  gap:10px;
}

.activity-item {
  padding:14px 16px;
  border:1px solid var(--line);
  border-radius:var(--radius-sm);
  background:var(--paper);
}

.activity-item strong,
.activity-item span {
  display:block;
}

.activity-item span {
  color:var(--muted);
  font-size:.86rem;
  margin-top:4px;
}

.status {
  display:inline-flex;
  padding:5px 10px;
  border-radius:999px;
  font-size:.75rem;
  font-weight:700;
  text-transform:capitalize;
}

.status-paid,
.status-completed {
  background:var(--sage-soft);
  color:var(--forest);
}

.status-partial,
.status-in_progress {
  background:var(--gold-soft);
  color:#80622d;
}

.status-pending,
.status-open {
  background:#f1f3f2;
  color:var(--muted);
}

.status-overdue {
  background:#f8e5e5;
  color:var(--danger);
}

.attendance-register .toolbar {
  display:flex;
  gap:18px;
  flex-wrap:wrap;
  margin-bottom:24px;
}

.attendance-register label {
  display:grid;
  gap:7px;
  color:var(--muted);
  font-size:.85rem;
  font-weight:700;
}

@media (max-width:720px) {
  .page-header {
    display:block;
  }

  .page-header .btn {
    width:100%;
    margin-top:18px;
  }

  .intelligence-card {
    min-height:auto;
  }

  .table-wrap {
    overflow-x:auto;
  }

  table {
    min-width:720px;
  }
}
'''

write(CSS, css)

print("WORKFLOW IMPLEMENTATION COMPLETE")

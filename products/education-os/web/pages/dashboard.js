import { api } from "../js/api.js";
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

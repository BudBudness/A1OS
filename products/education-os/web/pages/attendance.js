import { api } from "../js/api.js";
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

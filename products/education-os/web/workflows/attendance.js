export function loadWorkflow(root){
    root.innerHTML = `<section id="attendance" data-workflow="attendance">
  <header>
    <h2>Attendance</h2>
    <button id="attendance-refresh" type="button">Refresh attendance</button>
  </header>

  <form id="attendance-record-form">
    <input name="student_id" type="number" placeholder="Student ID" required>
    <input name="attendance_date" type="date" required>
    <select name="status" required>
      <option value="present">Present</option>
      <option value="absent">Absent</option>
      <option value="late">Late</option>
      <option value="excused">Excused</option>
    </select>
    <input name="notes" placeholder="Notes">
    <button type="submit">Record attendance</button>
  </form>

  <div id="attendance-operation-status" role="status"></div>
  <div id="attendance-list" aria-live="polite"></div>
</section>

<script>
(function () {
  const ATTENDANCE_WORKFLOW_MARKER = "ATTENDANCE_WORKFLOW_V1";
  const TOKEN_KEY = "little_oaks_access_token";

  const status = document.getElementById("attendance-operation-status");
  const list = document.getElementById("attendance-list");
  const form = document.getElementById("attendance-record-form");
  const refresh = document.getElementById("attendance-refresh");

  function authHeaders() {
    const token = localStorage.getItem(TOKEN_KEY);
    return token ? { Authorization: \`Bearer ${token}\` } : {};
  }

  async function loadAttendance() {
    status.textContent = "Loading attendance…";

    const response = await fetch("/api/attendance", {
      headers: authHeaders(),
    });

    if (!response.ok) {
      status.textContent = \`Unable to load attendance (${response.status})\`;
      return;
    }

    const payload = await response.json();
    const records = Array.isArray(payload)
      ? payload
      : (payload.items || payload.attendance || []);

    list.innerHTML = records.map(record => \`
      <article class="attendance-record">
        <strong>Student #${record.student_id || "—"}</strong>
        <span>${record.status || "unknown"}</span>
        <small>
          ${record.attendance_date || record.date || ""}
          ${record.notes ? \` — ${record.notes}\` : ""}
        </small>
      </article>
    \`).join("") || "<p>No attendance records found.</p>";

    status.textContent = \`${records.length} attendance record(s) loaded.\`;

    window.dispatchEvent(new CustomEvent(
      "little-oaks-attendance-loaded",
      { detail: { count: records.length } }
    ));
  }

  form?.addEventListener("submit", async function (event) {
    event.preventDefault();

    const data = Object.fromEntries(new FormData(form).entries());

    status.textContent = "Recording attendance…";

    const response = await fetch("/api/attendance", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      status.textContent = \`Attendance recording failed (${response.status})\`;
      return;
    }

    form.reset();
    status.textContent = "Attendance recorded successfully.";
    await loadAttendance();
  });

  refresh?.addEventListener("click", loadAttendance);

  window.LITTLE_OAKS_STAGE_4_ATTENDANCE_WORKFLOW = true;
  window.LITTLE_OAKS_ATTENDANCE_WORKFLOW_MARKER =
    ATTENDANCE_WORKFLOW_MARKER;

  if (localStorage.getItem(TOKEN_KEY)) {
    loadAttendance();
  }
})();
</script>


<!-- LITTLE_OAKS_STAGE_4_FEES_BILLING_WORKFLOW -->
`;
}

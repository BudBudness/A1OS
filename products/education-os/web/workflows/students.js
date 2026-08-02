export function loadWorkflow(root){
    root.innerHTML = `<section id="students" data-workflow="student-operations">
  <header>
    <h2>Student Operations</h2>
    <button id="student-refresh" type="button">Refresh students</button>
  </header>

  <form id="student-create-form">
    <input name="full_name" placeholder="Student full name" required>
    <input name="date_of_birth" type="date">
    <input name="gender" placeholder="Gender">
    <button type="submit">Add student</button>
  </form>

  <div id="student-operation-status" role="status"></div>
  <div id="student-list" aria-live="polite"></div>
</section>

<script>
(function () {
  const STUDENT_WORKFLOW_MARKER = "STUDENT_OPERATIONS_WORKFLOW_V1";
  const TOKEN_KEY = "little_oaks_access_token";
  const status = document.getElementById("student-operation-status");
  const list = document.getElementById("student-list");
  const form = document.getElementById("student-create-form");
  const refresh = document.getElementById("student-refresh");

  function token() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function headers() {
    const t = token();
    return t ? { Authorization: \`Bearer ${t}\` } : {};
  }

  async function loadStudents() {
    status.textContent = "Loading students…";

    const response = await fetch("/api/students", {
      headers: headers(),
    });

    if (!response.ok) {
      status.textContent = \`Unable to load students (${response.status})\`;
      return;
    }

    const payload = await response.json();
    const students = Array.isArray(payload)
      ? payload
      : (payload.items || payload.students || []);

    list.innerHTML = students.map(student => \`
      <article class="student-record">
        <strong>${student.full_name || student.name || "Unnamed student"}</strong>
        <span>${student.student_number || student.id || ""}</span>
      </article>
    \`).join("") || "<p>No students found.</p>";

    status.textContent = \`${students.length} student record(s) loaded.\`;

    window.dispatchEvent(new CustomEvent(
      "little-oaks-student-operations-loaded",
      { detail: { count: students.length } }
    ));
  }

  form?.addEventListener("submit", async function (event) {
    event.preventDefault();

    const data = Object.fromEntries(new FormData(form).entries());

    status.textContent = "Creating student…";

    const response = await fetch("/api/students", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...headers(),
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      status.textContent = \`Student creation failed (${response.status})\`;
      return;
    }

    form.reset();
    status.textContent = "Student created successfully.";
    await loadStudents();
  });

  refresh?.addEventListener("click", loadStudents);

  window.LITTLE_OAKS_STAGE_4_STUDENT_OPERATIONS_WORKFLOW = true;
  window.LITTLE_OAKS_STUDENT_OPERATIONS_WORKFLOW_MARKER =
    STUDENT_WORKFLOW_MARKER;

  if (token()) {
    loadStudents();
  }
})();
</script>


<!-- LITTLE_OAKS_STAGE_4_ADMISSIONS_WORKFLOW -->
`;
}

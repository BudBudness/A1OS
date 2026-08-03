export function loadWorkflow(root){
    root.innerHTML = `<section id="admissions" data-workflow="admissions">
  <header>
    <h2>Admissions</h2>
    <button id="admissions-refresh" type="button">Refresh admissions</button>
  </header>

  <form id="admission-create-form">
    <input name="student_name" placeholder="Applicant full name" required>
    <input name="date_of_birth" type="date">
    <input name="parent_name" placeholder="Parent / guardian name">
    <input name="parent_phone" placeholder="Parent / guardian phone">
    <select name="status">
      <option value="pending">Pending</option>
      <option value="approved">Approved</option>
      <option value="rejected">Rejected</option>
    </select>
    <button type="submit">Create admission</button>
  </form>

  <div id="admission-operation-status" role="status"></div>
  <div id="admission-list" aria-live="polite"></div>
</section>`;


  const ADMISSIONS_WORKFLOW_MARKER = "ADMISSIONS_WORKFLOW_V1";
  const TOKEN_KEY = "little_oaks_access_token";

  const status = document.getElementById("admission-operation-status");
  const list = document.getElementById("admission-list");
  const form = document.getElementById("admission-create-form");
  const refresh = document.getElementById("admissions-refresh");

  function authHeaders() {
    const token = localStorage.getItem(TOKEN_KEY);
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async function loadAdmissions() {
    status.textContent = "Loading admissions…";

    const response = await fetch("/api/admissions", {
      headers: authHeaders(),
    });

    if (!response.ok) {
      status.textContent = `Unable to load admissions (${response.status})`;
      return;
    }

    const payload = await response.json();
    const admissions = Array.isArray(payload)
      ? payload
      : (payload.items || payload.admissions || []);

    list.innerHTML = admissions.map(admission => `
      <article class="admission-record">
        <strong>
          ${admission.student_name || admission.full_name || "Unnamed applicant"}
        </strong>
        <span>${admission.status || "pending"}</span>
        <small>${admission.parent_name || ""}</small>
      </article>
    `).join("") || "<p>No admissions found.</p>";

    status.textContent = `${admissions.length} admission record(s) loaded.`;

    window.dispatchEvent(new CustomEvent(
      "little-oaks-admissions-loaded",
      { detail: { count: admissions.length } }
    ));
  }

  form?.addEventListener("submit", async function (event) {
    event.preventDefault();

    const data = Object.fromEntries(new FormData(form).entries());

    status.textContent = "Creating admission…";

    const response = await fetch("/api/admissions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      status.textContent = `Admission creation failed (${response.status})`;
      return;
    }

    form.reset();
    status.textContent = "Admission created successfully.";
    await loadAdmissions();
  });

  refresh?.addEventListener("click", loadAdmissions);

  window.LITTLE_OAKS_STAGE_4_ADMISSIONS_WORKFLOW = true;
  window.LITTLE_OAKS_ADMISSIONS_WORKFLOW_MARKER =
    ADMISSIONS_WORKFLOW_MARKER;

  if (localStorage.getItem(TOKEN_KEY)) {
    loadAdmissions();
  }




}

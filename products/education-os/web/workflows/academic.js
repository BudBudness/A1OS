export function loadWorkflow(root){
    root.innerHTML = `<section id="academic-operations-workflow" class="workflow-panel">
  <div class="section-heading">
    <div>
      <span class="eyebrow">ACADEMIC OPERATIONS</span>
      <h2>Academic Structure</h2>
      <p>Manage academic years, periods, and class levels from the director workspace.</p>
    </div>
    <button id="academic-refresh-btn" class="secondary-btn">Refresh</button>
  </div>

  <div class="workflow-grid">
    <article class="workflow-card">
      <h3>Academic Years</h3>
      <div id="academic-years-list">
        <div class="empty-state">Loading academic years...</div>
      </div>
    </article>

    <article class="workflow-card">
      <h3>Academic Periods</h3>
      <div id="academic-periods-list">
        <div class="empty-state">Loading academic periods...</div>
      </div>
    </article>

    <article class="workflow-card">
      <h3>Class Levels</h3>
      <div id="class-levels-list">
        <div class="empty-state">Loading class levels...</div>
      </div>
    </article>
  </div>

  <div id="academic-workflow-status" class="workflow-status"></div>
</section>`;


  const ACADEMIC_OPERATIONS_WORKFLOW_V1 = true;
  const tokenKey = "a1os_access_token";

  function authHeaders() {
    const token = localStorage.getItem(tokenKey);
    return token
      ? { "Authorization": `Bearer ${token}` }
      : {};
  }

  async function fetchAcademic(path) {
    const response = await fetch(path, {
      headers: authHeaders()
    });

    if (!response.ok) {
      throw new Error(`${path} returned ${response.status}`);
    }

    return response.json();
  }

  function itemsFrom(payload) {
    if (Array.isArray(payload)) return payload;
    return payload.items || payload.data || payload.results || [];
  }

  function renderList(elementId, payload, emptyText) {
    const element = document.getElementById(elementId);
    const items = itemsFrom(payload);

    if (!items.length) {
      element.innerHTML = `<div class="empty-state">${emptyText}</div>`;
      return;
    }

    element.innerHTML = items.map(item => {
      const name =
        item.name ||
        item.title ||
        item.label ||
        item.year ||
        item.class_name ||
        item.level_name ||
        "Unnamed";

      const status = item.status
        ? `<span class="status-badge">${item.status}</span>`
        : "";

      return `
        <div class="academic-item">
          <strong>${name}</strong>
          ${status}
        </div>
      `;
    }).join("");
  }

  async function loadAcademicOperations() {
    const status = document.getElementById("academic-workflow-status");

    try {
      const [years, periods, classLevels] = await Promise.all([
        fetchAcademic("/academic/years"),
        fetchAcademic("/academic/periods"),
        fetchAcademic("/academic/class-levels")
      ]);

      renderList(
        "academic-years-list",
        years,
        "No academic years found."
      );

      renderList(
        "academic-periods-list",
        periods,
        "No academic periods found."
      );

      renderList(
        "class-levels-list",
        classLevels,
        "No class levels found."
      );

      status.textContent = "Academic operations loaded successfully.";
      status.className = "workflow-status success";

      window.dispatchEvent(new CustomEvent(
        "little-oaks-academic-operations-loaded",
        {
          detail: {
            years,
            periods,
            classLevels
          }
        }
      ));
    } catch (error) {
      status.textContent =
        "Unable to load academic operations. Please verify authentication and API availability.";
      status.className = "workflow-status error";
      console.error("Academic operations workflow error:", error);
    }
  }

  const refreshButton =
    document.getElementById("academic-refresh-btn");

  if (refreshButton) {
    refreshButton.addEventListener(
      "click",
      loadAcademicOperations
    );
  }

  window.addEventListener(
    "little-oaks-dashboard-data-loaded",
    loadAcademicOperations
  );

  window.addEventListener(
    "little-oaks-live-dashboard-rendered",
    loadAcademicOperations
  );

  window.LITTLE_OAKS_ACADEMIC_OPERATIONS_WORKFLOW =
    loadAcademicOperations;

  if (ACADEMIC_OPERATIONS_WORKFLOW_V1) {
    setTimeout(loadAcademicOperations, 0);
  }


// END STAGE_4_ACADEMIC_OPERATIONS_WORKFLOW_V1


// STAGE_4_REPORTS_WORKFLOW_V1
}

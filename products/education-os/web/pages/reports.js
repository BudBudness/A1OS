export async function loadReports(api) {
  const response = await api.operations.list();
  if (!response.ok) throw new Error("Failed to load reports");
  return response.json();
}

export function renderReports(container, data = {}) {
  container.innerHTML = `
    <section class="reports-page">
      <h1>Reports & Intelligence</h1>
      <div class="report-grid">
        <article><h3>Students</h3><strong>${data.students_count ?? 0}</strong></article>
        <article><h3>Admissions</h3><strong>${data.admissions_count ?? 0}</strong></article>
        <article><h3>Attendance</h3><strong>${data.attendance_count ?? 0}</strong></article>
        <article><h3>Operations</h3><strong>${data.operations_count ?? 0}</strong></article>
      </div>
    </section>
  `;
}

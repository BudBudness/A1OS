import { api } from "../js/api.js";
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

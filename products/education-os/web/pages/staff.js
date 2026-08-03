import { api } from "../js/education-api.js";
import { can } from "../js/auth.js?v=1785434576";

export async function renderStaffPage() {
  try {
    const response = await api.intelligence.staff();
    const staff = Array.isArray(response) ? response : (response.staff || []);

    const roles = [...new Set(staff.map(s => s.role).filter(Boolean))];

    return `
      <div class="page-header">
        <div>
          <span class="eyebrow">PEOPLE & OPERATIONS</span>
          <h2>Staff & HR</h2>
          <p class="page-subtitle">Manage the Little Oaks team, roles, status, and access.</p>
        </div>
        ${can("staff.manage") ? `<button class="button button-primary">Add Staff</button>` : ""}
      </div>

      <section class="grid-3 intelligence-metrics">
        <div class="card">
          <span>Active Staff</span>
          <strong>${staff.length}</strong>
        </div>
        <div class="card">
          <span>Roles</span>
          <strong>${roles.length}</strong>
        </div>
        <div class="card">
          <span>Visible Results</span>
          <strong>${staff.length}</strong>
        </div>
      </section>

      <section class="card">
        <div class="table-wrap">
          ${
            staff.length
            ? `
            <table class="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Email</th>
                </tr>
              </thead>
              <tbody>
                ${staff.map(member => `
                  <tr>
                    <td>${member.full_name || "-"}</td>
                    <td>${(member.role || "-").replaceAll("_"," ")}</td>
                    <td>${member.email || "-"}</td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
            `
            : `<div class="empty">No staff found.</div>`
          }
        </div>
      </section>
    `;

  } catch (err) {
    return `
      <div class="card">
        <h3>Unable to load staff</h3>
        <p>${err.message}</p>
      </div>
    `;
  }
}

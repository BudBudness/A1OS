import { api } from "../js/api.js";
import { user, can } from "../js/auth.js";

export async function renderStaffPage() {
  const root = document.querySelector("#page-content");
  root.innerHTML = `
    <section class="page-header">
      <div>
        <span class="eyebrow">PEOPLE & OPERATIONS</span>
        <h1>Staff & HR</h1>
        <p>Manage the Little Oaks team, roles, status, and access.</p>
      </div>
      ${can("staff.manage") ? `<button class="button button-primary" id="add-staff">Add Staff</button>` : ""}
    </section>

    <section class="stat-grid" id="staff-stats"></section>

    <section class="panel">
      <div class="panel-header">
        <div>
          <h2>Staff Directory</h2>
          <p>Active staff members and operational roles.</p>
        </div>
        <div class="toolbar">
          <input id="staff-search" class="input" type="search" placeholder="Search staff">
          <select id="staff-role-filter" class="input">
            <option value="">All roles</option>
          </select>
        </div>
      </div>
      <div id="staff-table"></div>
    </section>
  `;

  const response = await api.intelligence.staff();
  const staff = Array.isArray(response) ? response : (response.staff || []);

  const roles = [...new Set(staff.map((member) => member.role).filter(Boolean))];
  const roleFilter = document.querySelector("#staff-role-filter");

  roles.forEach((role) => {
    const option = document.createElement("option");
    option.value = role;
    option.textContent = role.replaceAll("_", " ");
    roleFilter.appendChild(option);
  });

  const render = () => {
    const search = document.querySelector("#staff-search").value.toLowerCase();
    const role = roleFilter.value;

    const filtered = staff.filter((member) => {
      const matchesSearch =
        !search ||
        member.full_name.toLowerCase().includes(search) ||
        (member.email || "").toLowerCase().includes(search);

      const matchesRole = !role || member.role === role;

      return matchesSearch && matchesRole;
    });

    document.querySelector("#staff-stats").innerHTML = `
      <article class="stat-card">
        <span class="stat-label">Active Staff</span>
        <strong>${staff.length}</strong>
      </article>
      <article class="stat-card">
        <span class="stat-label">Roles</span>
        <strong>${roles.length}</strong>
      </article>
      <article class="stat-card">
        <span class="stat-label">Visible Results</span>
        <strong>${filtered.length}</strong>
      </article>
    `;

    document.querySelector("#staff-table").innerHTML = filtered.length
      ? `
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Role</th>
                <th>Email</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              ${filtered.map((member) => `
                <tr>
                  <td><strong>${member.full_name}</strong></td>
                  <td><span class="badge">${member.role.replaceAll("_", " ")}</span></td>
                  <td>${member.email || "—"}</td>
                  <td>
                    ${can("staff.manage")
                      ? `<button class="button button-small" data-staff-id="${member.id}">Manage</button>`
                      : "—"}
                  </td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      `
      : `<div class="empty-state"><h3>No staff found</h3><p>Try changing your search or role filter.</p></div>`;
  };

  document.querySelector("#staff-search").addEventListener("input", render);
  roleFilter.addEventListener("change", render);
  render();
}

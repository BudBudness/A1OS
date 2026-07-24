import { api } from "../js/api.js";

export async function renderAdmissions() {
    const admissions = await api.admissions.list();

    return `
        <section class="card">
            <div class="toolbar">
                <h2 class="section-title">Admissions</h2>
                <button class="btn btn-primary" id="new-admission">
                    + New Admission
                </button>
            </div>

            ${
                admissions.length
                    ? `
                        <div class="table-wrap">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Reference</th>
                                        <th>Applicant</th>
                                        <th>Class</th>
                                        <th>Status</th>
                                        <th>Created</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${admissions
                                        .map(
                                            a => `
                                                <tr>
                                                    <td>${a.application_reference || "—"}</td>
                                                    <td>${[a.first_name, a.last_name].filter(Boolean).join(" ") || a.applicant_name || "—"}</td>
                                                    <td>${a.class_name || a.requested_class || "—"}</td>
                                                    <td>
                                                        <span class="status status-success">
                                                            ${a.status || "submitted"}
                                                        </span>
                                                    </td>
                                                    <td>${a.created_at || "—"}</td>
                                                </tr>
                                            `
                                        )
                                        .join("")}
                                </tbody>
                            </table>
                        </div>
                    `
                    : "<div class='empty'>No admissions yet.</div>"
            }
        </section>
    `;
}

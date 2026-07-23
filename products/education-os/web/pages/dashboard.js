import { api } from "../js/api.js";
import { metric, loading, error } from "../js/components/ui.js";

export async function renderDashboard() {
    try {
        const [students, admissions] = await Promise.all([
            api.students.list(),
            api.admissions.list()
        ]);

        return `
            <div class="grid grid-4">
                ${metric("Total Students", students.length)}
                ${metric("Admissions", admissions.length)}
                ${metric("Fees & Payments", "—")}
                ${metric("Attendance", "—")}
            </div>

            <br>

            <div class="grid grid-2">
                <section class="card">
                    <h2 class="section-title">Recent Admissions</h2>
                    ${
                        admissions.length
                            ? `
                                <div class="table-wrap">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Applicant</th>
                                                <th>Class</th>
                                                <th>Status</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${admissions
                                                .slice(0, 10)
                                                .map(
                                                    a => `
                                                        <tr>
                                                            <td>${a.applicant_name || "—"}</td>
                                                            <td>${a.requested_class || a.class_name || "—"}</td>
                                                            <td>
                                                                <span class="status status-success">
                                                                    ${a.status || "submitted"}
                                                                </span>
                                                            </td>
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

                <section class="card">
                    <h2 class="section-title">Quick Actions</h2>
                    <div class="grid grid-2">
                        <button class="btn btn-primary" data-route="students">
                            Register Student
                        </button>
                        <button class="btn btn-primary" data-route="admissions">
                            New Admission
                        </button>
                        <button class="btn btn-secondary" data-route="fees">
                            Record Payment
                        </button>
                        <button class="btn btn-secondary" data-route="attendance">
                            Mark Attendance
                        </button>
                    </div>
                </section>
            </div>
        `;
    } catch (e) {
        return error(e.message);
    }
}

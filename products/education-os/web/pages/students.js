import { api } from "../js/api.js";

export async function renderStudents() {
    const students = await api.students.list();

    return `
        <section class="card">
            <div class="toolbar">
                <h2 class="section-title">Student Registry</h2>
                <button class="btn btn-primary" id="register-student">
                    + Register Student
                </button>
            </div>

            <div class="table-wrap">
                ${
                    students.length
                        ? `
                            <table>
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Name</th>
                                        <th>Date of Birth</th>
                                        <th>Gender</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${students
                                        .map(
                                            s => `
                                                <tr>
                                                    <td>${s.id}</td>
                                                    <td>${s.first_name || ""} ${s.last_name || ""}</td>
                                                    <td>${s.date_of_birth || "—"}</td>
                                                    <td>${s.gender || "—"}</td>
                                                </tr>
                                            `
                                        )
                                        .join("")}
                                </tbody>
                            </table>
                        `
                        : "<div class='empty'>No students registered yet.</div>"
                }
            </div>
        </section>
    `;
}

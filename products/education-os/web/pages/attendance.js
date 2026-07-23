import { api } from "../js/api.js";

export async function renderAttendance() {
    try {
        const attendance = await api.attendance.list();

        return `
            <section class="card">
                <div class="toolbar">
                    <h2 class="section-title">Attendance</h2>
                    <button class="btn btn-primary">+ Mark Attendance</button>
                </div>
                ${
                    attendance.length
                        ? "<div class='table-wrap'>Attendance data loaded.</div>"
                        : "<div class='empty'>No attendance records yet.</div>"
                }
            </section>
        `;
    } catch (e) {
        return `<div class="error">${e.message}</div>`;
    }
}

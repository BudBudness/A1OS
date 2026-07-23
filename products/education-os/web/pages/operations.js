import { api } from "../js/api.js";

export async function renderOperations() {
    try {
        const operations = await api.operations.list();

        return `
            <section class="card">
                <div class="toolbar">
                    <h2 class="section-title">School Operations</h2>
                    <button class="btn btn-primary">+ New Operation</button>
                </div>
                ${
                    operations.length
                        ? "<div class='table-wrap'>Operations data loaded.</div>"
                        : "<div class='empty'>No school operations recorded yet.</div>"
                }
            </section>
        `;
    } catch (e) {
        return `<div class="error">${e.message}</div>`;
    }
}

import { api } from "../js/api.js";

export async function renderFees() {
    try {
        const fees = await api.fees.list();

        return `
            <section class="card">
                <div class="toolbar">
                    <h2 class="section-title">Fees & Payments</h2>
                    <button class="btn btn-primary">+ Record Payment</button>
                </div>
                ${
                    fees.length
                        ? "<div class='table-wrap'>Fees data loaded.</div>"
                        : "<div class='empty'>No fee obligations recorded yet.</div>"
                }
            </section>
        `;
    } catch (e) {
        return `<div class="error">${e.message}</div>`;
    }
}

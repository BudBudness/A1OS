import { api } from "../js/api.js";
import { error, loading } from "../js/components/ui.js";

const money = value =>
  `UGX ${Number(value || 0).toLocaleString("en-UG")}`;

export async function renderFees() {
  try {
    const fees = await api.fees.list();

    return `
      <div class="page-header">
        <div>
          <span class="eyebrow">Finance</span>
          <h2>Fees & Payments</h2>
          <p class="page-subtitle">Manage obligations, collections, balances and payment history.</p>
        </div>
        <button class="btn btn-primary" id="record-payment">+ Record Payment</button>
      </div>

      <div class="card">
        <div class="table-wrap">
          ${
            fees.length
              ? `<table>
                  <thead>
                    <tr>
                      <th>Student</th>
                      <th>Fee Type</th>
                      <th>Academic Period</th>
                      <th>Amount</th>
                      <th>Paid</th>
                      <th>Balance</th>
                      <th>Status</th>
                      <th>Due Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${fees.map(f => {
                      const balance = Math.max(
                        Number(f.amount || 0) -
                        Number(f.amount_paid || 0), 0
                      );

                      const status =
                        balance <= 0 ? "paid" :
                        f.due_date &&
                        new Date(f.due_date) < new Date()
                          ? "overdue" :
                        Number(f.amount_paid || 0) > 0
                          ? "partial" : "pending";

                      return `
                        <tr>
                          <td>${f.first_name || ""} ${f.last_name || ""}</td>
                          <td>${f.fee_type || "—"}</td>
                          <td>${f.academic_period || "—"}</td>
                          <td>${money(f.amount)}</td>
                          <td>${money(f.amount_paid)}</td>
                          <td>${money(balance)}</td>
                          <td><span class="status status-${status}">${status}</span></td>
                          <td>${f.due_date || "—"}</td>
                        </tr>
                      `;
                    }).join("")}
                  </tbody>
                </table>`
              : `<div class="empty">No fee obligations recorded yet.</div>`
          }
        </div>
      </div>
    `;
  } catch (err) {
    return error(err.message);
  }
}

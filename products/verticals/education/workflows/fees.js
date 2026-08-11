export function loadWorkflow(root){
    root.innerHTML = `<section id="fees" data-workflow="fees-billing">
  <header>
    <h2>Fees & Billing</h2>
    <button id="fees-refresh" type="button">Refresh billing</button>
  </header>

  <form id="fee-record-form">
    <input name="student_id" type="number" placeholder="Student ID" required>
    <input name="amount" type="number" min="0" step="0.01" placeholder="Amount" required>
    <select name="currency">
      <option value="UGX">UGX</option>
    </select>
    <input name="description" placeholder="Fee description" required>
    <input name="due_date" type="date">
    <select name="status">
      <option value="pending">Pending</option>
      <option value="paid">Paid</option>
      <option value="overdue">Overdue</option>
    </select>
    <button type="submit">Create fee record</button>
  </form>

  <div id="fees-operation-status" role="status"></div>
  <div id="fees-summary" aria-live="polite"></div>
  <div id="fees-list" aria-live="polite"></div>
</section>`;





}



  const FEES_BILLING_WORKFLOW_MARKER = "FEES_BILLING_WORKFLOW_V1";
  const TOKEN_KEY = "little_oaks_access_token";

  const status = document.getElementById("fees-operation-status");
  const summary = document.getElementById("fees-summary");
  const list = document.getElementById("fees-list");
  const form = document.getElementById("fee-record-form");
  const refresh = document.getElementById("fees-refresh");

  function authHeaders() {
    const token = localStorage.getItem(TOKEN_KEY);
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  function amountValue(record) {
    return Number(
      record.amount ??
      record.amount_due ??
      record.total ??
      0
    );
  }

  function formatAmount(record) {
    const amount = amountValue(record);
    const currency = record.currency || "UGX";

    return new Intl.NumberFormat("en-UG", {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
    }).format(amount);
  }

  async function loadFees() {
    status.textContent = "Loading billing records…";

    const response = await fetch("/api/fees", {
      headers: authHeaders(),
    });

    if (!response.ok) {
      status.textContent = `Unable to load billing records (${response.status})`;
      return;
    }

    const payload = await response.json();
    const records = Array.isArray(payload)
      ? payload
      : (payload.items || payload.fees || payload.billing || []);

    const total = records.reduce(
      (sum, record) => sum + amountValue(record),
      0
    );

    const paid = records
      .filter(record => (record.status || "").toLowerCase() === "paid")
      .reduce((sum, record) => sum + amountValue(record), 0);

    const outstanding = total - paid;

    summary.innerHTML = `
      <strong>Total billed: UGX ${total.toLocaleString("en-UG")}</strong>
      <span>Paid: UGX ${paid.toLocaleString("en-UG")}</span>
      <span>Outstanding: UGX ${outstanding.toLocaleString("en-UG")}</span>
    `;

    list.innerHTML = records.map(record => `
      <article class="fee-record">
        <strong>Student #${record.student_id || "-"}</strong>
        <span>${record.description || "Fee record"}</span>
        <b>${formatAmount(record)}</b>
        <small>
          ${record.status || "pending"}
          ${record.due_date ? ` - Due ${record.due_date}` : ""}
        </small>
      </article>
    `).join("") || "<p>No billing records found.</p>";

    status.textContent = `${records.length} billing record(s) loaded.`;

    window.dispatchEvent(new CustomEvent(
      "little-oaks-fees-billing-loaded",
      {
        detail: {
          count: records.length,
          total,
          paid,
          outstanding,
        },
      }
    ));
  }

  form?.addEventListener("submit", async function (event) {
    event.preventDefault();

    const data = Object.fromEntries(new FormData(form).entries());

    status.textContent = "Creating fee record…";

    const response = await fetch("/api/fees", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      status.textContent = `Fee record creation failed (${response.status})`;
      return;
    }

    form.reset();
    status.textContent = "Fee record created successfully.";
    await loadFees();
  });

  refresh?.addEventListener("click", loadFees);

  window.LITTLE_OAKS_STAGE_4_FEES_BILLING_WORKFLOW = true;
  window.LITTLE_OAKS_FEES_BILLING_WORKFLOW_MARKER =
    FEES_BILLING_WORKFLOW_MARKER;

  if (localStorage.getItem(TOKEN_KEY)) {
    loadFees();
  }

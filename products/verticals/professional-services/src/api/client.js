const API_BASE = import.meta.env.VITE_A1OS_API_BASE || "";

async function request(path, options = {}) {
  const session =
    globalThis.__A1OS_SESSION__ ||
    globalThis.__A1OS_AUTH__ ||
    null;

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (session?.token) headers.Authorization = `Bearer ${session.token}`;

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    const body = await response.text().catch(() => "");
    throw new Error(body || `API ${response.status}`);
  }

  const type = response.headers.get("content-type") || "";
  return type.includes("application/json")
    ? response.json()
    : response.text();
}

const crud = (resource) => ({
  list: () => request(`/v1/professional-services/${resource}`),
  get: (id) => request(`/v1/professional-services/${resource}/${id}`),
  create: (data) =>
    request(`/v1/professional-services/${resource}`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id, data) =>
    request(`/v1/professional-services/${resource}/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  remove: (id) =>
    request(`/v1/professional-services/${resource}/${id}`, {
      method: "DELETE",
    }),
});

export const a1osApi = {
  health: () => request("/v1/health"),
  clients: crud("clients"),
  projects: crud("projects"),
  quotes: crud("quotes"),
  invoices: crud("invoices"),
  payments: crud("payments"),
  tasks: crud("tasks"),
  documents: crud("documents"),
  settings: crud("settings"),
  audit: () => request("/v1/professional-services/audit"),
  reports: {
    financial: () =>
      request("/v1/professional-services/reports/financial"),
    receivables: () =>
      request("/v1/professional-services/reports/receivables"),
  },
  convertQuoteToInvoice: (quoteId) =>
    request(
      `/v1/professional-services/quotes/${quoteId}/convert-to-invoice`,
      { method: "POST" }
    ),
};

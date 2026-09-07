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

  if (session?.token) {
    headers.Authorization = `Bearer ${session.token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    const body = await response.text().catch(() => "");
    throw new Error(body || `A1OS API error: ${response.status}`);
  }

  const type = response.headers.get("content-type") || "";
  return type.includes("application/json")
    ? response.json()
    : response.text();
}

export const a1osApi = {
  health: () => request("/v1/health"),

  projects: {
    list: () => request("/v1/professional-services/projects"),
    get: (id) => request(`/v1/professional-services/projects/${id}`),
    create: (data) =>
      request("/v1/professional-services/projects", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    update: (id, data) =>
      request(`/v1/professional-services/projects/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    remove: (id) =>
      request(`/v1/professional-services/projects/${id}`, {
        method: "DELETE",
      }),
  },

  clients: {
    list: () => request("/v1/professional-services/clients"),
    get: (id) => request(`/v1/professional-services/clients/${id}`),
    create: (data) =>
      request("/v1/professional-services/clients", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    update: (id, data) =>
      request(`/v1/professional-services/clients/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    remove: (id) =>
      request(`/v1/professional-services/clients/${id}`, {
        method: "DELETE",
      }),
  },
  quotes: {
    list: () => request("/v1/professional-services/quotes"),
    get: (id) => request(`/v1/professional-services/quotes/${id}`),
    create: (data) =>
      request("/v1/professional-services/quotes", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    update: (id, data) =>
      request(`/v1/professional-services/quotes/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    remove: (id) =>
      request(`/v1/professional-services/quotes/${id}`, {
        method: "DELETE",
      }),
  },

  invoices: {
    list: () => request("/v1/professional-services/invoices"),
    get: (id) => request(`/v1/professional-services/invoices/${id}`),
    create: (data) =>
      request("/v1/professional-services/invoices", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    update: (id, data) =>
      request(`/v1/professional-services/invoices/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    remove: (id) =>
      request(`/v1/professional-services/invoices/${id}`, {
        method: "DELETE",
      }),
    convertQuote: (quoteId) =>
      request(
        `/v1/professional-services/quotes/${quoteId}/convert-to-invoice`,
        { method: "POST" }
      ),
  },

};

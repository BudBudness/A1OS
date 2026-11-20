const base = import.meta.env.VITE_LEGAL_API_BASE || "/api";
async function request(path, options = {}) {
  const response = await fetch(`${base}${path}`, {
    credentials: "same-origin",
    cache: "no-store",
    ...options,
    headers: { ...(options.body instanceof FormData ? {} : { "content-type": "application/json" }), ...(options.headers || {}) }
  });
  const payload = response.status === 204 ? null : await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(payload?.error || `Request failed (${response.status})`);
    error.status = response.status;
    throw error;
  }
  return payload;
}
export const api = {
  session: () => request("/session"),
  workspace: () => request("/workspace"),
  createClient: (body) => request("/clients", { method: "POST", body: JSON.stringify(body) }),
  createMatter: (body) => request("/matters", { method: "POST", body: JSON.stringify(body) })
};

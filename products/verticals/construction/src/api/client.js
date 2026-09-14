const base = globalThis.__A1OS_API_BASE__ || "/v1";

async function request(path, options = {}) {
  const response = await fetch(`${base}${path}`, {
    headers: {"Content-Type": "application/json", ...(options.headers || {})},
    credentials: "include",
    ...options
  });
  if (!response.ok) throw new Error(`A1OS API ${response.status}: ${await response.text()}`);
  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  get: path => request(path),
  post: (path, body) => request(path, {method:"POST", body:JSON.stringify(body)}),
  patch: (path, body) => request(path, {method:"PATCH", body:JSON.stringify(body)}),
  delete: path => request(path, {method:"DELETE"})
};

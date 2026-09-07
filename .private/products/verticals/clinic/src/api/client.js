const baseUrl =
  globalThis.__A1OS_PLATFORM_API_URL__ ||
  import.meta?.env?.VITE_A1OS_PLATFORM_API_URL ||
  "/api";

export const api = {
  provider: "a1os-platform-api",
  baseUrl,

  async request(path, options = {}) {
    const response = await fetch(`${baseUrl}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {})
      }
    });

    if (!response.ok) {
      throw new Error(`A1OS Platform API request failed: ${response.status}`);
    }

    if (response.status === 204) {
      return null;
    }

    return response.json();
  },

  get(path, options = {}) {
    return this.request(path, { ...options, method: "GET" });
  },

  post(path, body, options = {}) {
    return this.request(path, {
      ...options,
      method: "POST",
      body: JSON.stringify(body)
    });
  },

  patch(path, body, options = {}) {
    return this.request(path, {
      ...options,
      method: "PATCH",
      body: JSON.stringify(body)
    });
  },

  delete(path, options = {}) {
    return this.request(path, { ...options, method: "DELETE" });
  }
};

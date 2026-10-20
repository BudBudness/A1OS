const baseUrl =
  globalThis.__A1OS_PLATFORM_API_URL__ ||
  import.meta.env.VITE_A1OS_PLATFORM_API_URL ||
  "/api";

async function request(path, options = {}) {
  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });
  if (response.status === 401) throw new Error("AUTH_REQUIRED");
  if (response.status === 403) throw new Error("ACCESS_DENIED");
  if (response.status === 404) throw new Error("PLATFORM_ENDPOINT_UNAVAILABLE");
  if (!response.ok) throw new Error(`PLATFORM_API_ERROR_${response.status}`);
  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  baseUrl,
  get: (path) => request(path),
  post: (path, body) => request(path, { method: "POST", body: JSON.stringify(body) }),
  patch: (path, body) => request(path, { method: "PATCH", body: JSON.stringify(body) })
};

export function getErrorMessage(error) {
  const code = error?.message;
  if (code === "AUTH_REQUIRED") return "Sign in through A1OS to access operational records.";
  if (code === "ACCESS_DENIED") return "Your A1OS role does not permit this action.";
  if (code === "PLATFORM_ENDPOINT_UNAVAILABLE") return "The car-wash API contract is not yet available on this environment. Live operations are disabled.";
  if (code?.startsWith("PLATFORM_API_ERROR_")) return `The platform API returned ${code.replace("PLATFORM_API_ERROR_", "HTTP ")}.`;
  return "The platform API could not be reached. Check connectivity and try again.";
}

import { api } from "../api/client.js";

let principal = globalThis.__A1OS_PRINCIPAL__ || null;

export async function loadSession() {
  try {
    const data = await api.get("/auth/me");
    principal = data?.user || data?.principal || data || null;
    globalThis.__A1OS_PRINCIPAL__ = principal;
    globalThis.__A1OS_TENANT__ = principal?.tenant || {
      id: principal?.organization_id || principal?.tenant_id || null
    };
    globalThis.__A1OS_ROLE__ =
      principal?.role || principal?.role_name || "Owner";
    globalThis.__A1OS_PERMISSIONS__ =
      principal?.permissions || principal?.permission_names || [];
    return principal;
  } catch {
    principal = null;
    globalThis.__A1OS_PRINCIPAL__ = null;
    return null;
  }
}

export async function login(email,password) {
  const data = await api.post("/auth/login",{email,password});
  principal = data?.user || data?.principal || null;
  globalThis.__A1OS_PRINCIPAL__ = principal;
  globalThis.__A1OS_TENANT__ = data?.tenant || principal?.tenant || {
    id: data?.organization_id || principal?.organization_id ||
       data?.tenant_id || principal?.tenant_id || null
  };
  globalThis.__A1OS_ROLE__ =
    data?.role || principal?.role || principal?.role_name || "Owner";
  globalThis.__A1OS_PERMISSIONS__ =
    data?.permissions || principal?.permissions ||
    principal?.permission_names || [];
  return data;
}

export async function logout() {
  await api.post("/auth/logout",{});
  principal=null;
  globalThis.__A1OS_PRINCIPAL__=null;
  globalThis.__A1OS_TENANT__=null;
  globalThis.__A1OS_ROLE__=null;
  globalThis.__A1OS_PERMISSIONS__=[];
}

export function hasPermission(permission) {
  return (globalThis.__A1OS_PERMISSIONS__ || []).includes(permission);
}
export function currentRole() {
  return globalThis.__A1OS_ROLE__ || null;
}
export function isAuthenticated() {
  return Boolean(globalThis.__A1OS_PRINCIPAL__);
}
export function can(permission) {
  return isAuthenticated() && hasPermission(permission);
}
export function currentPrincipal() {
  return principal || globalThis.__A1OS_PRINCIPAL__ || null;
}

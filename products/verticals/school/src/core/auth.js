export function hasPermission(permission) {
  return (globalThis.__A1OS_PERMISSIONS__ || []).includes(permission);
}

export function currentRole() {
  return globalThis.__A1OS_ROLE__ || "Owner";
}

export function isAuthenticated() {
  return Boolean(globalThis.__A1OS_PRINCIPAL__);
}

export function can(permission) {
  return isAuthenticated() && hasPermission(permission);
}

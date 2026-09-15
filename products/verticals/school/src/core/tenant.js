export function tenant() {
  return globalThis.__A1OS_TENANT__ || null;
}

export function tenantId() {
  return tenant()?.id || tenant()?.tenant_id || null;
}

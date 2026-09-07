export const permissions = {
  owner: "a1os-core",

  has(permission) {
    const current =
      globalThis.__A1OS_PERMISSIONS__ || [];

    return current.includes(permission);
  }
};

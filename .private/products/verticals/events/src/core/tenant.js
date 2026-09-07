export const tenant = {
  owner: "a1os-core",

  getCurrent() {
    return globalThis.__A1OS_TENANT__ || null;
  }
};

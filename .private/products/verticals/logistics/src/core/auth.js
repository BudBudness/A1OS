export const auth = {
  owner: "a1os-core",

  getSession() {
    return globalThis.__A1OS_SESSION__ || null;
  },

  isAuthenticated() {
    return Boolean(this.getSession());
  }
};

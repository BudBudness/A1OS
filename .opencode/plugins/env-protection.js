export const EnvProtection = async () => {
  const looksSecret = (p = "") => {
    const s = String(p).replace(/\\/g, "/").toLowerCase();
    if (s.includes("cfg/storage.key")) return true;
    if (s.includes("/secrets/")) return true;
    if (s.endsWith(".key") || s.endsWith(".secret") || s.endsWith(".pem") || s.endsWith(".p12")) return true;
    if (s.includes("/.env") || s.startsWith(".env")) {
      return !s.endsWith(".example");
    }
    return false;
  };

  return {
    "tool.execute.before": async (input, output) => {
      const path = output.args?.filePath || output.args?.path || output.args?.file || "";
      if (looksSecret(path)) {
        throw new Error(
          `Blocked by env-protection plugin: refusing to ${input.tool} secret file ${path}`
        );
      }
    },
  };
};

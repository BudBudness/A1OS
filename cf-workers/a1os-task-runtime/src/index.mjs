import { D1TaskStore } from "./d1-task-store.mjs";
import { processTaskBatch } from "./process-task-batch.mjs";

export async function runScheduledBatch(env) {
  if (!env.A1OS_EXECUTOR_URL || !env.A1OS_D1_EXECUTOR_TOKEN) {
    throw new Error("Staging executor URL and token are required");
  }
  const endpoint = new URL(env.A1OS_EXECUTOR_URL);
  if (endpoint.protocol !== "https:" || endpoint.username || endpoint.password ||
      endpoint.pathname !== "/internal/d1-task-health" || endpoint.search || endpoint.hash) {
    throw new Error("Expected the HTTPS staging executor endpoint");
  }

  return processTaskBatch(new D1TaskStore(env.DB), async task => {
    if (task.target !== "a1os" || task.role !== "operator" || task.action !== "health") {
      return { error: "ApprovalDenied: only staging health tasks are supported" };
    }
    const response = await fetch(endpoint, {
      method: "POST",
      redirect: "error",
      signal: AbortSignal.timeout(10_000),
      headers: {
        "Content-Type": "application/json",
        "X-A1OS-Executor-Token": env.A1OS_D1_EXECUTOR_TOKEN,
      },
      body: JSON.stringify(task),
    });
    if (response.status === 204) return { status: "completed" };
    await response.body?.cancel();
    return { error: `Staging executor returned HTTP ${response.status}` };
  });
}

export default {
  async scheduled(_controller, env) {
    const counts = await runScheduledBatch(env);
    console.log(JSON.stringify({ event: "a1os_staging_task_batch", ...counts }));
  },
};

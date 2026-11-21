import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";

const base = (process.env.A1OS_QUEUE_URL || "http://127.0.0.1:8787").replace(/\/$/, "");
const token = process.env.A1OS_QUEUE_TOKEN;
if (!token) throw new Error("A1OS_QUEUE_TOKEN is required");
const workerDir = process.env.A1OS_QUEUE_WORKER_DIR || process.cwd();
const database = process.env.A1OS_QUEUE_LOCAL_DB || "a1os-task-queue-integration";
const headers = { authorization: `Bearer ${token}`, "content-type": "application/json" };
const id = (label) => `http-${label}-${crypto.randomUUID().replaceAll("-", "")}`;
const request = async (path, method = "GET", body) => {
  const response = await fetch(base + path, {
    method,
    headers,
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  return { status: response.status, data: await response.json() };
};
const enqueue = async (taskId, maxAttempts = 3) => request("/v1/tasks", "POST", {
  task_id: taskId, target: "staging", role: "integration", action: "noop",
  payload: { suite: "http-lifecycle" }, max_attempts: maxAttempts,
});
const setStale = (taskId) => {
  const sql = `UPDATE tasks SET updated_at=datetime('now','-600 seconds') WHERE task_id='${taskId}' AND status='running'`;
  const result = spawnSync("npx", [
    "wrangler", "d1", "execute", database, "--local", "--config", "wrangler.integration.json",
    "--command", sql,
  ], { cwd: workerDir, encoding: "utf8" });
  if (result.status !== 0) {
    throw new Error(`Could not age local integration task: ${result.stderr || result.stdout}`);
  }
};

async function main() {
  const unauth = await fetch(base + "/v1/tasks/pending");
  assert.equal(unauth.status, 401, "queue endpoints require authentication");

  const sameId = id("idempotent");
  const payload = { task_id: sameId, target: "staging", role: "integration", action: "noop", payload: { suite: "http-lifecycle" }, max_attempts: 3 };
  let r = await request("/v1/tasks", "POST", payload);
  assert.equal(r.status, 201, "first enqueue creates task");
  r = await request("/v1/tasks", "POST", payload);
  assert.equal(r.status, 200, "same idempotency key and content returns existing task");
  assert.equal(r.data.created, false);
  r = await request("/v1/tasks", "POST", { ...payload, action: "different" });
  assert.equal(r.status, 409, "same idempotency key with different content conflicts");

  const concurrentId = id("concurrent");
  r = await enqueue(concurrentId);
  assert.equal(r.status, 201);
  const claims = await Promise.all([
    request(`/v1/tasks/${concurrentId}/claim`, "POST", {}),
    request(`/v1/tasks/${concurrentId}/claim`, "POST", {}),
  ]);
  assert.deepEqual(claims.map((x) => x.status).sort(), [200, 409], "exactly one concurrent claimant wins");
  const winner = claims.find((x) => x.status === 200);
  assert.equal(winner.data.task.status, "running");
  r = await request(`/v1/tasks/${concurrentId}/complete`, "POST", {});
  assert.equal(r.status, 200);
  assert.equal(r.data.task.status, "completed");
  assert.equal((await request(`/v1/tasks/${concurrentId}/claim`, "POST", {})).status, 409, "completed task cannot be reclaimed");

  const exhaustedId = id("exhausted");
  assert.equal((await enqueue(exhaustedId, 1)).status, 201);
  assert.equal((await request(`/v1/tasks/${exhaustedId}/claim`, "POST", {})).status, 200);
  r = await request(`/v1/tasks/${exhaustedId}/fail`, "POST", { error: "transient failure" });
  assert.equal(r.status, 200);
  assert.equal(r.data.task.status, "failed", "retry exhaustion becomes terminal");

  const staleRetryId = id("stale-retry");
  assert.equal((await enqueue(staleRetryId, 3)).status, 201);
  assert.equal((await request(`/v1/tasks/${staleRetryId}/claim`, "POST", {})).status, 200);
  setStale(staleRetryId);
  r = await request("/v1/tasks/recover", "POST", { stale_after_seconds: 30, limit: 100 });
  assert.equal(r.status, 200);
  assert.ok(r.data.tasks.some((task) => task.task_id === staleRetryId && task.status === "retry"), "stale running task returns to retry");
  r = await request(`/v1/tasks/${staleRetryId}`);
  assert.equal(r.status, 200);
  assert.equal(r.data.data.status, "retry");

  const staleTerminalId = id("stale-terminal");
  assert.equal((await enqueue(staleTerminalId, 1)).status, 201);
  assert.equal((await request(`/v1/tasks/${staleTerminalId}/claim`, "POST", {})).status, 200);
  setStale(staleTerminalId);
  r = await request("/v1/tasks/recover", "POST", { stale_after_seconds: 30, limit: 100 });
  assert.equal(r.status, 200);
  assert.ok(r.data.tasks.some((task) => task.task_id === staleTerminalId && task.status === "failed"), "stale task at retry limit becomes failed");

  console.log("PASS: HTTP auth, idempotency replay/conflict, atomic concurrent claim, completion, retry exhaustion, stale retry recovery, stale terminal recovery");
}

main().catch((error) => {
  console.error(`FAIL: ${error.stack || error.message || error}`);
  process.exitCode = 1;
});

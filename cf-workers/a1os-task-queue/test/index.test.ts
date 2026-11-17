import { describe, expect, it } from "vitest";
import worker from "../src/index";

const env = { DB: {} as never, TASK_QUEUE_TOKEN: "test-token", A1OS_E2E_TEST_TOKEN: "smoke-token" };

describe("A1OS D1 task queue Worker", () => {
  it("exposes a minimal health endpoint", async () => {
    const response = await worker.fetch(new Request("https://queue.test/health"), env);
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ ok: true, service: "a1os-d1-task-queue" });
  });

  it("rejects unauthenticated queue access before touching D1", async () => {
    const response = await worker.fetch(new Request("https://queue.test/v1/tasks", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ target: "research", role: "analyst", action: "scan", payload: {} }),
    }), env);
    expect(response.status).toBe(401);
    expect(await response.json()).toEqual({ error: "Unauthorized" });
  });

  it("rejects unsupported methods", async () => {
    const response = await worker.fetch(new Request("https://queue.test/health", { method: "POST" }), env);
    expect(response.status).toBe(405);
  });
  it("restricts the secondary token to acceptance-test tasks", async () => {
    const request = (path: string, method = "GET", body?: object) =>
      worker.fetch(new Request("https://queue.test" + path, {
        method,
        headers: { authorization: "Bearer smoke-token", "content-type": "application/json" },
        ...(body ? { body: JSON.stringify(body) } : {}),
      }), env);
    expect((await request("/v1/tasks/pending")).status).toBe(403);
    expect((await request("/v1/tasks/recover", "POST")).status).toBe(403);
    expect((await request("/v1/tasks/unrelated")).status).toBe(403);
    expect((await request("/v1/tasks", "POST", {
      task_id: "a1os-acceptance-" + "a".repeat(32),
      target: "production", role: "smoke", action: "noop", payload: { test: true },
    })).status).toBe(403);
    // An allowed smoke read reaches the DB (which is deliberately a stub here).
    expect((await request("/v1/tasks/a1os-acceptance-" + "a".repeat(32))).status).toBe(503);
  });

});

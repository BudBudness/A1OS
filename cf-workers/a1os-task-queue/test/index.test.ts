import { describe, expect, it } from "vitest";
import worker from "../src/index";

const env = { DB: {} as never, TASK_QUEUE_TOKEN: "test-token" };

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
    expect(response.status).toBe(404);
  });
});

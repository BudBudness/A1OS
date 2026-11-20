import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";

test("health endpoint is public and identifies the service", async () => {
  const response = await worker.fetch(new Request("https://legal.example/health"), {
    DB: {}, DOCUMENTS: {}, ACCESS_TEAM_DOMAIN: "example.cloudflareaccess.com", ACCESS_AUD: "test-aud"
  });
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { ok: true, service: "barya-legal-api" });
});

test("API requires a Cloudflare Access identity", async () => {
  const response = await worker.fetch(new Request("https://legal.example/api/session"), {
    DB: {}, DOCUMENTS: {}, ACCESS_TEAM_DOMAIN: "example.cloudflareaccess.com", ACCESS_AUD: "test-aud"
  });
  assert.equal(response.status, 401);
  assert.match((await response.json()).error, /authentication required/i);
});

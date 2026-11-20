import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
const root = new URL("../", import.meta.url);
test("Legal frontend has no Supabase SDK or credentials", async () => {
  const [pkg, env, app, api] = await Promise.all([
    readFile(new URL("package.json", root), "utf8"),
    readFile(new URL(".env.example", root), "utf8"),
    readFile(new URL("src/App.jsx", root), "utf8"),
    readFile(new URL("src/lib/api.js", root), "utf8")
  ]);
  assert.doesNotMatch(pkg, /supabase/i);
  assert.doesNotMatch(env, /supabase/i);
  assert.doesNotMatch(app, /supabase/i);
  assert.match(app, /Cloudflare Access/);
  assert.match(api, /credentials: "same-origin"/);
});
test("Cloudflare Worker verifies Access JWT and scopes matter records", async () => {
  const worker = await readFile(new URL("worker/src/index.js", root), "utf8");
  assert.match(worker, /jwtVerify/);
  assert.match(worker, /ACCESS_AUD/);
  assert.match(worker, /matter_members/);
  assert.match(worker, /DOCUMENTS/);
});

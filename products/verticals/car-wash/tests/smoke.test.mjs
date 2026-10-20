import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const root = new URL("../", import.meta.url);

test("vertical contract keeps platform-owned security and persistence", async () => {
  const contract = JSON.parse(await readFile(new URL("A1OS_VERTICAL.json", root), "utf8"));
  assert.equal(contract.type, "frontend-vertical");
  assert.equal(contract.ownership.authentication, "a1os-core");
  assert.equal(contract.ownership.tenancy, "a1os-core");
  assert.equal(contract.ownership.authorization, "a1os-core");
  assert.equal(contract.ownership.persistence, "a1os-platform");
  assert.equal(contract.scope.branches, 1);
  assert.equal(contract.scope.washCapacity, 4);
});

test("UI does not contain fake/demo business records or browser persistence", async () => {
  const app = await readFile(new URL("src/App.jsx", root), "utf8");
  assert.match(app, /\/car-wash\/dashboard/);
  assert.match(app, /\/car-wash\/vehicles/);
  assert.match(app, /\/car-wash\/parking/);
  assert.doesNotMatch(app, /localStorage|sessionStorage/);
  assert.doesNotMatch(app, /demo data|sample records/i);
});

test("API client enforces credentials and exposes authorization failures", async () => {
  const client = await readFile(new URL("src/api/client.js", root), "utf8");
  assert.match(client, /credentials: "include"/);
  assert.match(client, /AUTH_REQUIRED/);
  assert.match(client, /ACCESS_DENIED/);
});

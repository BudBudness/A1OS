import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";

test("vertical frontend contract", () => {
  const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
  assert.equal(fs.existsSync(path.join(root, "index.html")), true);
  assert.equal(fs.existsSync(path.join(root, "App.jsx")), true);
  assert.equal(fs.existsSync(path.join(root, "main.jsx")), true);
});

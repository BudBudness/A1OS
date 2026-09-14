import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

test("vertical frontend contract", () => {
  assert.equal(fs.existsSync("index.html"), true);
  assert.equal(fs.existsSync("App.jsx"), true);
  assert.equal(fs.existsSync("main.jsx"), true);
});

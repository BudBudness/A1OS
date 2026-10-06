import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

test("legal vertical has product constitution", () => {
  assert.equal(fs.existsSync(new URL("../PRODUCT_CONSTITUTION.md", import.meta.url)), true);
});

test("legal vertical has runtime entrypoint", () => {
  assert.equal(fs.existsSync(new URL("../src/App.jsx", import.meta.url)), true);
});

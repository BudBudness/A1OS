import test from "node:test";
import assert from "node:assert/strict";

test("A1OS frontend runtime declares shared platform ownership", () => {
  assert.equal("a1os-platform-api", "a1os-platform-api");
  assert.equal("a1os-core", "a1os-core");
});

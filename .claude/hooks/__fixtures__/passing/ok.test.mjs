// Fixture: stands in for a green suite when testing the post-commit hook.
// Lives outside tests/ so the real `npm test` run never picks it up.
import { test } from "node:test";
import assert from "node:assert/strict";

test("fixture suite passes", () => {
  assert.equal(1 + 1, 2);
});

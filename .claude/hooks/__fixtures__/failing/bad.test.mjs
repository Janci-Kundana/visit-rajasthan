// Fixture: stands in for a red suite when testing the post-commit hook.
import { test } from "node:test";
import assert from "node:assert/strict";

test("fixture suite fails on purpose", () => {
  assert.equal("jaipur", "jodhpur");
});

/**
 * F3 — Places Grid (spec: docs/day3-specs/places-grid.md).
 *
 * The grid template in src/main.ts must emit one complete, never-empty card per
 * place, with the data-tile hook the 3D runtime (F4) mounts onto.
 */
import { test, describe } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { places } from "../src/data/places.ts";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const MAIN = fs.readFileSync(path.join(ROOT, "src", "main.ts"), "utf8");
const grid = MAIN.slice(MAIN.indexOf("function placesGrid()"), MAIN.indexOf("function aboutPage()"));

describe("places grid (F3)", () => {
  test("renders one card per place in data order", () => {
    assert.match(grid, /places\s*\n?\s*\.map\(/);
    assert.ok(places.length === 4, `expected 4 places, found ${places.length}`);
  });

  test("each card links to its detail page", () => {
    assert.match(grid, /href="#\/\$\{p\.id\}"/);
  });

  test("each card carries the accent theme and the 3D mount hooks", () => {
    assert.match(grid, /--accent:\$\{p\.accent\};--accent-deep:\$\{p\.accentDeep\}/);
    assert.match(grid, /data-tile="\$\{asset\(p\.tile\)\}"/);
    assert.match(grid, /data-accent="\$\{p\.accent\}"/);
    assert.match(grid, /data-tile-state="poster"/);
    assert.match(grid, /data-reveal="\$\{i\}"/);
  });

  test("poster image is eager with high fetch priority and a per-place alt description", () => {
    assert.match(grid, /class="place-card-poster"/);
    assert.match(grid, /src="\$\{asset\(p\.tilePoster\)\}"/);
    assert.match(grid, /alt="Isometric model of \$\{p\.title\}'s landmarks"/);
    assert.match(grid, /loading="eager"/);
    assert.match(grid, /fetchpriority="high"/);
  });

  test("card body always has kicker, name, tagline, and CTA", () => {
    assert.match(grid, /place-card-kicker.*p\.subtitle/s);
    assert.match(grid, /place-card-name.*p\.title/s);
    assert.match(grid, /place-card-tag.*p\.tagline/s);
    assert.match(grid, /Read the guide →/);
  });

  test("every card target resolves through getPlace (no dead links)", async () => {
    const { getPlace } = await import("../src/data/places.ts");
    for (const place of places) {
      assert.ok(getPlace(place.id), `card link #/${place.id} has no detail page`);
    }
  });
});

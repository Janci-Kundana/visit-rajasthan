/**
 * Content checks for the four destinations the site is built around.
 *
 * These exist so the post-commit hook has something worth running: every entry in
 * places.ts points at a hero photo, a Blender-built .glb tile and its poster PNG,
 * and a missing asset only shows up as a blank card at runtime. Catching it at
 * commit time is considerably cheaper.
 */
import { test, describe } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { places, getPlace } from "../src/data/places.ts";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const PUBLIC = path.join(ROOT, "public");

describe("places data", () => {
  test("ships the four destinations the nav expects, with unique ids", () => {
    const ids = places.map((place) => place.id);
    assert.deepEqual(ids.slice().sort(), ["jaipur", "jaisalmer", "jawai", "udaipur"]);
    assert.equal(new Set(ids).size, ids.length, "place ids must be unique — routing keys off them");
  });

  test("every referenced asset exists under public/", () => {
    for (const place of places) {
      for (const field of ["hero", "tile", "tilePoster"]) {
        const asset = place[field];
        assert.ok(asset, `${place.id}.${field} is empty`);
        assert.ok(
          !asset.startsWith("/"),
          `${place.id}.${field} must stay relative so the GitHub Pages base URL applies`,
        );
        assert.ok(
          fs.existsSync(path.join(PUBLIC, asset)),
          `${place.id}.${field} points at missing asset public/${asset}`,
        );
      }
    }
  });

  test("accent colours are valid hex, so the per-page tint cannot silently break", () => {
    for (const place of places) {
      for (const field of ["accent", "accentDeep"]) {
        assert.match(place[field], /^#[0-9a-f]{6}$/i, `${place.id}.${field} is not a hex colour`);
      }
    }
  });

  test("each destination page has enough content to render", () => {
    for (const place of places) {
      assert.ok(place.title.length > 0, `${place.id} has no title`);
      assert.ok(place.lede.length > 120, `${place.id} lede is too thin for the hero block`);
      assert.ok(place.stats.length >= 3, `${place.id} needs at least 3 stats for the fact strip`);
      assert.ok(place.sections.length >= 1, `${place.id} has no prose sections`);
      assert.ok(place.highlights.length >= 1, `${place.id} has no highlights`);
      assert.ok(place.seasons.length >= 1, `${place.id} has no season guidance`);
    }
  });

  test("getPlace resolves known ids and rejects everything else", () => {
    assert.equal(getPlace("udaipur")?.title, "Udaipur");
    assert.equal(getPlace("jawai")?.id, "jawai");
    assert.equal(getPlace("jodhpur"), undefined);
    assert.equal(getPlace(undefined), undefined);
  });
});

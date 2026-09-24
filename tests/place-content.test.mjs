/**
 * F7 depth — Content Data (spec: docs/day3-specs/content-data.md).
 *
 * Companion to the existing tests/places.test.mjs (ids, asset existence, hex
 * accents, minimum content, getPlace). These cases cover the depth the detail
 * page (F5) needs: every block's data present and non-empty for every place.
 */
import { test, describe } from "node:test";
import assert from "node:assert/strict";

import { places, getPlace } from "../src/data/places.ts";

describe("place content depth (F7)", () => {
  test("every place has identity, hero, and traveller-note fields", () => {
    for (const place of places) {
      for (const field of ["subtitle", "tagline", "hero", "tile", "tilePoster", "heroCredit", "mindful"]) {
        assert.ok(place[field]?.length > 0, `${place.id}.${field} is empty`);
      }
    }
  });

  test("heroFocus is a valid CSS object-position", () => {
    for (const place of places) {
      assert.match(place.heroFocus, /^(center|left|right|top|bottom|\d+%)(\s+(center|top|bottom|\d+%))?$/);
    }
  });

  test("prose sections have headings and non-empty bodies", () => {
    for (const place of places) {
      assert.ok(place.sections.length >= 1, `${place.id} has no prose sections`);
      for (const section of place.sections) {
        assert.ok(section.heading.length > 0, `${place.id} has an untitled section`);
        assert.ok(section.body.length >= 1, `${place.id} section "${section.heading}" has no body`);
        for (const paragraph of section.body) {
          assert.ok(paragraph.length > 40, `${place.id} section "${section.heading}" has a stub paragraph`);
        }
      }
    }
  });

  test("highlights and experiences carry name, meta, and text", () => {
    for (const place of places) {
      for (const list of ["highlights", "experiences"]) {
        assert.ok(place[list].length >= 1, `${place.id} has no ${list}`);
        for (const item of place[list]) {
          assert.ok(item.name?.length > 0, `${place.id}.${list} has an unnamed item`);
          assert.ok(item.text?.length > 40, `${place.id}.${list} "${item.name}" text is a stub`);
        }
      }
    }
  });

  test("seasons and festivals are complete enough to plan around", () => {
    for (const place of places) {
      assert.ok(place.seasons.length >= 1, `${place.id} has no season guidance`);
      for (const season of place.seasons) {
        assert.ok(season.months?.length > 0, `${place.id} season missing months`);
        assert.ok(season.label?.length > 0, `${place.id} season missing label`);
      }
      assert.ok(place.festivals.length >= 1, `${place.id} has no festivals`);
      for (const festival of place.festivals) {
        assert.ok(festival.name?.length > 0, `${place.id} festival missing name`);
        assert.ok(festival.when?.length > 0, `${place.id} festival "${festival.name}" missing date`);
        assert.ok(festival.text?.length > 40, `${place.id} festival "${festival.name}" text is a stub`);
      }
    }
  });

  test("food, practical, and mindful blocks are non-empty", () => {
    for (const place of places) {
      assert.ok(place.food.length >= 1, `${place.id} has no food entries`);
      for (const item of place.food) {
        assert.ok(item?.length > 0, `${place.id} has an empty food entry`);
      }
      assert.ok(place.practical.length >= 1, `${place.id} has no practical rows`);
      for (const row of place.practical) {
        assert.ok(row?.label?.length > 0, `${place.id} has an unlabeled practical row`);
        assert.ok(row?.value?.length > 0, `${place.id} practical row "${row?.label}" has no value`);
      }
      assert.ok(place.mindful.length > 80, `${place.id} mindful note is a stub`);
    }
  });

  test("stats carry non-empty label and value pairs", () => {
    for (const place of places) {
      for (const stat of place.stats) {
        assert.ok(stat?.label?.length > 0, `${place.id} has a stat with no label`);
        assert.ok(stat?.value?.length > 0, `${place.id} stat "${stat?.label}" has no value`);
      }
    }
  });

  test("getPlace never throws and rejects empties", () => {
    assert.doesNotThrow(() => getPlace());
    assert.equal(getPlace(), undefined);
    assert.doesNotThrow(() => getPlace(""));
    assert.equal(getPlace(""), undefined);
    assert.equal(getPlace("JAIPUR"), undefined);
    assert.equal(getPlace(" jaipur "), undefined);
  });

  test("getPlace never throws for non-string, wrong-shape input", () => {
    for (const badId of [null, 42, true, {}, [], () => {}]) {
      assert.doesNotThrow(() => getPlace(badId));
      assert.equal(getPlace(badId), undefined);
    }
  });
});

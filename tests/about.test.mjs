/**
 * F6 — About Page (spec: docs/day3-specs/about-page.md).
 *
 * The colophon must state what the site covers, how the 3D is built, and who to
 * credit — and must not grow destination-page blocks or start 3D runtimes.
 */
import { test, describe } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const MAIN = fs.readFileSync(path.join(ROOT, "src", "main.ts"), "utf8");
const about = MAIN.slice(MAIN.indexOf("function aboutPage()"), MAIN.indexOf("function placePage("));
const route = MAIN.slice(
  MAIN.indexOf("function route()"),
  MAIN.indexOf('window.addEventListener("hashchange", route)'),
);
const showPage = MAIN.slice(MAIN.indexOf("function showPage("), MAIN.indexOf("function route()"));

describe("about page (F6)", () => {
  test("renders in the narrow shell as Colophon / About Us", () => {
    assert.match(about, /page-shell narrow/);
    assert.match(about, /page-kicker">Colophon/);
    assert.match(about, /page-heading">About Us/);
  });

  test("states the four-place scope and the no-filler editorial line", () => {
    for (const city of ["Jaisalmer", "Jaipur", "Udaipur", "Jawai"]) {
      assert.ok(about.includes(city), `coverage statement missing ${city}`);
    }
    assert.match(about, /guide to four destinations/);
    assert.match(about, /none of the filler/i);
    assert.match(about, /four places properly than\s*twenty badly/i);
  });

  test("explains both 3D builds and their still fallbacks", () => {
    assert.match(about, /Hawa Mahal/);
    assert.match(about, /Blender interpretation/);
    assert.match(about, /Three\.js renders the façade live/);
    assert.match(about, /rendered still of the same model/);
    assert.match(about, /isometric tile/);
    assert.match(about, /modelled in Blender/);
    assert.match(about, /tiles load as real models/);
    assert.match(about, /rendered still of the same scene/);
  });

  test("credits photography, type, and stack", () => {
    assert.match(about, /Pinterest/);
    assert.match(about, /Cormorant Garamond and Inter/);
    assert.match(about, /Vite, TypeScript and Three\.js/);
  });

  test("mounts no 3D and stays a colophon, not a fifth destination", () => {
    assert.doesNotMatch(about, /data-tile/);
    assert.doesNotMatch(about, /class="fact-strip"/);
    assert.doesNotMatch(about, /class="season-row"/);
    // "practical logistics" appears in the intro copy; what must not appear is
    // the destination-style practical table block.
    assert.doesNotMatch(about, /class="practical"/);
    assert.doesNotMatch(about, /<table/);
  });

  test("the about route stops the home scene and unmounts tiles without mounting new ones", () => {
    assert.match(
      route,
      /scene\.setActive\(false\);\s*if \(resolution\.type === "about"\) \{[\s\S]*?showPage\(aboutPage\(\)\)/,
    );
    assert.match(showPage, /unmountTileCards\(\)/);
    assert.doesNotMatch(about, /mountTileCards|requestAnimationFrame|new THREE\./);
  });
  test("about route never mounts tile cards, unlike the places-grid fallback route", () => {
    const aboutBranch = route.slice(
      route.indexOf(String.raw`if (resolution.type === "about")`),
      route.indexOf(String.raw`if (resolution.type === "place")`),
    );
    assert.doesNotMatch(aboutBranch, /mountTileCards\(/);
    assert.match(route, /mountTileCards\(pageContent, pageContent\)/);
  });

  test("about page carries no destination-style highlights, timeline, food list, or mindful blocks", () => {
    assert.doesNotMatch(about, /class="hl-grid"/);
    assert.doesNotMatch(about, /class="timeline"/);
    assert.doesNotMatch(about, /class="food-list"/);
    assert.doesNotMatch(about, /class="mindful"/);
  });
});

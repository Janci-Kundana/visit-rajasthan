/**
 * F8 — UX & Accessibility Plumbing (spec: docs/day3-specs/ux-accessibility.md).
 *
 * Cross-cutting cases: hidden panels stay out of the keyboard path, decorative
 * 3D stays out of the accessibility tree, images load at the right priority,
 * and exactly one surface is ever visible.
 */
import { test, describe } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const MAIN = fs.readFileSync(path.join(ROOT, "src", "main.ts"), "utf8");
const INDEX = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");
const SCENE = fs.readFileSync(path.join(ROOT, "src", "three", "HomeScene.ts"), "utf8");
const TILE = fs.readFileSync(path.join(ROOT, "src", "three", "TileCard.ts"), "utf8");

describe("ux and accessibility (F8)", () => {
  test("hidden panels are inert; shown panels are not", () => {
    assert.match(MAIN, /homeHero\.inert = true/);
    assert.match(MAIN, /pageContent\.inert = true/);
    assert.match(MAIN, /homeHero\.inert = false/);
    assert.match(MAIN, /pageContent\.inert = false/);
  });

  test("reset hides both panels so only one surface can show", () => {
    const route = MAIN.slice(MAIN.indexOf("function route()"));
    const resetEnd = route.indexOf('if (resolution.type === "home")');
    const reset = route.slice(0, resetEnd);
    assert.match(reset, /homeHero\.classList\.add\("hidden"\)/);
    assert.match(reset, /pageContent\.classList\.add\("hidden"\)/);
  });

  test("home body state and panel visibility follow the home route", () => {
    const route = MAIN.slice(MAIN.indexOf("function route()"));
    assert.match(
      route,
      /document\.body\.classList\.toggle\("on-home", resolution\.type === "home"\)/,
    );
    assert.match(
      route,
      /if \(resolution\.type === "home"\) \{[\s\S]*?homeHero\.classList\.remove\("hidden"\)[\s\S]*?return;/,
    );
    assert.match(
      MAIN,
      /function showPage\(html: string\) \{[\s\S]*?pageContent\.classList\.remove\("hidden"\)/,
    );
  });

  test("home canvas is hidden from assistive tech; home container toggles with it", () => {
    assert.match(SCENE, /renderer\.domElement\.setAttribute\("aria-hidden", "true"\)/);
    assert.match(SCENE, /this\.container\.setAttribute\("aria-hidden", String\(!active\)\)/);
  });

  test("home poster has meaningful alt text", () => {
    assert.match(SCENE, /this\.poster\.alt\s*=\s*"[^"]{20,}"/);
  });

  test("decorative tile canvases are hidden from assistive tech", () => {
    assert.match(TILE, /canvas\.setAttribute\("aria-hidden", "true"\)/);
  });

  test("tile animation loops pause when the tab is hidden", () => {
    assert.match(TILE, /document\.addEventListener\("visibilitychange"/);
    assert.match(TILE, /document\.hidden/);
  });

  test("tile posters carry per-place alt text", () => {
    assert.match(MAIN, /alt="Isometric model of \$\{p\.title\}'s landmarks"/);
  });

  test("decorative arrows in the shell are aria-hidden", () => {
    assert.ok(INDEX.includes('<span aria-hidden="true">↗</span>'));
    assert.ok(INDEX.includes('<span aria-hidden="true">→</span>'));
  });

  test("image priorities are set: home poster eager, tile posters lazy", () => {
    assert.match(SCENE, /this\.poster\.fetchPriority = "high"/);
    assert.match(MAIN, /loading="lazy"/);
  });

  test("both 3D runtimes honour reduced motion", () => {
    assert.match(SCENE, /prefers-reduced-motion: reduce/);
    assert.match(TILE, /prefers-reduced-motion: reduce/);
    assert.match(SCENE, /const visible = this\.active && !document\.hidden && this\.ready/);
    assert.match(SCENE, /this\.renderer\.setAnimationLoop\(animate \? this\.tick : null\)/);
    assert.match(
      TILE,
      /if \(reducedMotion\.matches\) \{[\s\S]*?if \(!this\.stillRendered\) \{[\s\S]*?this\.renderFrame\(\);[\s\S]*?this\.stillRendered = true;[\s\S]*?\}\s*return;\s*\}[\s\S]*?this\.raf = requestAnimationFrame\(loop\)/,
    );
  });

  test("loading screen is dismissed on home, named, detail, and fallback routes", () => {
    const route = MAIN.slice(MAIN.indexOf("function route()"));
    assert.equal((route.match(/dismissLoader\(\);/g) ?? []).length, 4);
  });

  test("nav route states cover home, places, about, and no active place-page item", () => {
    for (const route of ["home", "places", "about"]) {
      assert.ok(INDEX.includes(`data-route="${route}"`), `nav has no ${route} route`);
      assert.ok(MAIN.includes(`setActiveNav("${route}")`), `${route} route is not activated`);
    }
    assert.ok(
      MAIN.includes('setActiveNav("")'),
      "place pages should leave every nav item inactive",
    );
  });

  test("nav active state is exclusive by data-route", () => {
    assert.match(
      MAIN,
      /link\.classList\.toggle\("active", link\.getAttribute\("data-route"\) === route\)/,
    );
  });
});

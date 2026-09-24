/**
 * F1 — Routing & Navigation (spec: docs/day3-specs/routing-navigation.md).
 *
 * The pure hash resolver is exercised with concrete URL inputs. The browser
 * shell is checked structurally because main.ts imports CSS and Three.js.
 */
import { test, describe } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { resolveRoute } from "../src/router.ts";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const MAIN = fs.readFileSync(path.join(ROOT, "src", "main.ts"), "utf8");
const INDEX = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");

describe("routing (F1)", () => {
  test("the app resolves the current hash against the destination ids", () => {
    assert.match(
      MAIN,
      /resolveRoute\(\s*window\.location\.hash,\s*places\.map\(\(place\) => place\.id\)/s,
    );
  });

  test("home branch shows the hero, hides content, and activates the scene", () => {
    assert.match(MAIN, /if \(resolution\.type === "home"\) \{[^}]*setActiveNav\("home"\)/s);
    assert.match(MAIN, /if \(resolution\.type === "home"\) \{[^}]*scene\.setActive\(true\)/s);
    assert.match(MAIN, /homeHero\.classList\.remove\("hidden"\)/);
    assert.match(MAIN, /homeHero\.inert = false/);
    assert.match(
      MAIN,
      /document\.body\.classList\.toggle\("on-home", resolution\.type === "home"\)/,
    );
  });

  test("leaving home always deactivates the 3D scene", () => {
    const homeEnd = MAIN.indexOf('if (resolution.type === "home")');
    const deactivate = MAIN.indexOf("scene.setActive(false)");
    assert.ok(homeEnd !== -1 && deactivate !== -1 && deactivate > homeEnd);
  });

  test("about branch renders the colophon with active nav", () => {
    assert.match(MAIN, /if \(resolution\.type === "about"\) \{[^}]*setActiveNav\("about"\)/s);
    assert.match(MAIN, /if \(resolution\.type === "about"\) \{[^}]*showPage\(aboutPage\(\)\)/s);
  });

  test("known place ids render a detail page with parallax", () => {
    assert.match(MAIN, /if \(resolution\.type === "place"\) \{[^}]*getPlace\(resolution\.id\)/s);
    assert.match(MAIN, /showPage\(placePage\(place\)\)/);
    assert.match(MAIN, /if \(place\) \{[^}]*setActiveNav\(""\)/s);
    assert.match(MAIN, /attachHeroParallax\(\)/);
  });

  test("unknown hashes fall back to the places grid, never a blank page", () => {
    const fallback = MAIN.slice(MAIN.indexOf('if (resolution.type === "place")'));
    assert.match(fallback, /setActiveNav\("places"\)/);
    assert.match(fallback, /showPage\(placesGrid\(\)\)/);
    assert.match(fallback, /mountTileCards\(pageContent, pageContent\)/);
  });

  test("every route change disposes previous tiles before mounting new ones", () => {
    assert.match(MAIN, /function showPage\(html: string\) \{\s*\n\s*unmountTileCards\(\);/);
    assert.match(MAIN, /if \(resolution\.type === "home"\) \{\s*\n\s*unmountTileCards\(\);/);
  });

  test("loader dismisses on every branch including fallbacks", () => {
    const dismissals = MAIN.match(/dismissLoader\(\);/g) || [];
    // home + about + place + fallback = 4 branches minimum.
    assert.ok(dismissals.length >= 4, `expected 4+ dismissals, found ${dismissals.length}`);
  });

  test("router listens for back/forward and runs on first load", () => {
    assert.match(MAIN, /window\.addEventListener\("hashchange", route\)/);
    assert.ok(MAIN.trimEnd().endsWith("route();"));
  });

  test("reset state hides and deactivates both panels together", () => {
    assert.match(MAIN, /homeHero\.classList\.add\("hidden"\)/);
    assert.match(MAIN, /pageContent\.classList\.add\("hidden"\)/);
    assert.match(MAIN, /homeHero\.inert = true/);
    assert.match(MAIN, /pageContent\.inert = true/);
  });

  test("page transitions reveal and enable content after the reset", () => {
    assert.match(
      MAIN,
      /function showPage\(html: string\) \{[\s\S]*?pageContent\.innerHTML = html;[\s\S]*?pageContent\.inert = false;[\s\S]*?pageContent\.classList\.remove\("hidden"\)/,
    );
  });

  test("all non-home routes deactivate the scene before selecting a page", () => {
    const route = MAIN.slice(MAIN.indexOf("function route()"));
    assert.match(route, /scene\.setActive\(false\);\s*\n\s*if \(resolution\.type === "about"\)/);
    assert.match(route, /scene\.setActive\(false\);[\s\S]*?setActiveNav\("places"\)/);
  });

  test("every route outcome dismisses the loading screen", () => {
    const route = MAIN.slice(MAIN.indexOf("function route()"));
    for (const branch of [
      /if \(resolution\.type === "home"\) \{[^}]*dismissLoader\(\);/s,
      /if \(resolution\.type === "about"\) \{[^}]*dismissLoader\(\);/s,
      /if \(place\) \{[^}]*dismissLoader\(\);/s,
      /setActiveNav\("places"\);[\s\S]*?dismissLoader\(\);/,
    ]) {
      assert.match(route, branch);
    }
  });

  test("internal links use hash routes", () => {
    const htmlLinks = [...INDEX.matchAll(/<a\b[^>]*\bhref="([^"]+)"/g)];
    const templateLinks = [...MAIN.matchAll(/href="(#[^"]+)"/g)];
    assert.ok(htmlLinks.length > 0, "expected internal navigation links in index.html");
    assert.ok(templateLinks.length > 0, "expected internal links in route templates");
    for (const [, href] of [...htmlLinks, ...templateLinks]) {
      assert.ok(href.startsWith("#/"), `internal link must use a #/ route, found ${href}`);
    }
  });

  test("runtime asset attributes resolve through the base-path helper", () => {
    assert.match(MAIN, /const asset = \(path: string\) => import\.meta\.env\.BASE_URL \+ path/);
    const assetAttributes = [...MAIN.matchAll(/\b(?:src|data-tile)="\$\{([^}]+)\}"/g)];
    assert.ok(assetAttributes.length > 0, "expected runtime asset attributes in route templates");
    for (const [, expression] of assetAttributes) {
      if (expression === "mapEmbedUrl") continue;
      assert.ok(
        expression.startsWith("asset("),
        `runtime asset must use asset(), found ${expression}`,
      );
    }
  });

  test("shell markup provides the panels, nav routes, and loader the router needs", () => {
    for (const id of ["home-hero", "page-content", "primary-nav", "loading-screen"]) {
      assert.ok(INDEX.includes(`id="${id}"`), `index.html missing #${id}`);
    }
    for (const route of ['data-route="home"', 'data-route="places"', 'data-route="about"']) {
      assert.ok(INDEX.includes(route), `index.html nav missing ${route}`);
    }
  });
  test("the home branch keeps the hero visible and content hidden", () => {
    const homeStart = MAIN.indexOf('if (resolution.type === "home") {');
    const afterHome = MAIN.indexOf("scene.setActive(false)");
    assert.ok(homeStart !== -1 && afterHome !== -1 && afterHome > homeStart);
    const homeBlock = MAIN.slice(homeStart, afterHome);
    assert.ok(
      !homeBlock.includes('pageContent.classList.remove("hidden")'),
      "home must not unhide page-content",
    );
    assert.ok(
      !homeBlock.includes("pageContent.inert = false"),
      "home must keep page-content inert",
    );
    assert.ok(!homeBlock.includes("showPage("), "home must not render a detail page");
  });

  test("the home hero is revealed in exactly one place: the home branch", () => {
    const reveals = MAIN.match(/homeHero\.classList\.remove\("hidden"\)/g) || [];
    const enables = MAIN.match(/homeHero\.inert = false/g) || [];
    assert.equal(reveals.length, 1, "homeHero should only be unhidden on the home route");
    assert.equal(enables.length, 1, "homeHero should only be un-inerted on the home route");
  });

  test("no nav link matches an empty route, so known place pages show no active destination", () => {
    assert.ok(
      !INDEX.includes('data-route=""'),
      "a nav link with an empty data-route would force-highlight on place pages",
    );
  });
});

describe("route edge cases (F1)", () => {
  const placeIds = ["jaisalmer", "jaipur", "udaipur", "jawai"];

  test("empty hashes resolve to home", () => {
    for (const hash of ["", "#", "#/"]) {
      assert.deepEqual(
        resolveRoute(hash, placeIds),
        { type: "home" },
        `hash ${JSON.stringify(hash)}`,
      );
    }
  });

  test("every destination id resolves to its own guide", () => {
    for (const id of placeIds) {
      assert.deepEqual(resolveRoute(`#/${id}`, placeIds), { type: "place", id });
    }
  });

  test("known section routes resolve with one optional trailing slash", () => {
    assert.deepEqual(resolveRoute("#/places/", placeIds), { type: "places" });
    assert.deepEqual(resolveRoute("#/about/", placeIds), { type: "about" });
    assert.deepEqual(resolveRoute("#/jaipur/", placeIds), { type: "place", id: "jaipur" });
  });

  test("nested, malformed, and unknown routes fall back to the places grid", () => {
    for (const hash of ["#/places/jaipur", "#/jaipur//", "#/Jaipur", "#/jodhpur"]) {
      assert.deepEqual(
        resolveRoute(hash, placeIds),
        { type: "places" },
        `hash ${JSON.stringify(hash)}`,
      );
    }
  });
});

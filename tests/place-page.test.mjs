/**
 * F5 — Place Detail Page (spec: docs/day3-specs/place-detail-page.md).
 *
 * Structural cases over placePage() in src/main.ts: all thirteen content blocks in
 * order, accent theming, hero credit/crop, and cyclic next-place navigation.
 */
import { test, describe } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const MAIN = fs.readFileSync(path.join(ROOT, "src", "main.ts"), "utf8");
const CSS = fs.readFileSync(path.join(ROOT, "src", "style.css"), "utf8");
const page = MAIN.slice(
  MAIN.indexOf("function placePage("),
  MAIN.indexOf("function attachHeroParallax"),
);

describe("place detail page (F5)", () => {
  test("all thirteen content blocks render in order", () => {
    const blocks = [
      "place-hero",
      'class="lede"',
      "fact-strip",
      'class="prose"',
      "What to see",
      "Things to do",
      "When to go",
      "Festivals",
      "What to eat",
      "Know before you go",
      'class="block map-block"',
      'class="mindful"',
      "place-nav",
    ];
    let cursor = 0;
    for (const marker of blocks) {
      const at = page.indexOf(marker, cursor);
      assert.ok(at !== -1, `block missing or out of order: ${marker}`);
      cursor = at;
    }
  });

  test("page element is tinted from place data", () => {
    assert.match(
      page,
      /--accent:\$\{place\.accent\};--accent-deep:\$\{place\.accentDeep\};--focus:\$\{place\.heroFocus\}/,
    );
  });

  test("hero shows photo, credit, crumb, and titles", () => {
    assert.match(page, /class="place-hero-img" src="\$\{asset\(place\.hero\)\}"/);
    assert.match(page, /alt="\$\{place\.heroCredit\}"/);
    assert.match(page, /hero-credit.*place\.heroCredit/s);
    assert.match(page, /href="#\/places">← All destinations/);
    assert.match(page, /place-kicker.*place\.subtitle/s);
    assert.match(page, /place-title.*place\.title/s);
    assert.match(page, /place-tagline.*place\.tagline/s);
  });

  test("hero cropping uses the place's configured focus", () => {
    assert.match(page, /--focus:\$\{place\.heroFocus\}/);
    assert.match(CSS, /\.place-hero-img\s*\{[^}]*object-position:\s*var\(--focus, center\)/s);
  });

  test("fact strip, prose, and practical blocks map every data field", () => {
    assert.match(
      page,
      /place\.stats\.map\(\(s\) => `<div><dt>\$\{s\.label\}<\/dt><dd>\$\{s\.value\}<\/dd>/,
    );
    assert.match(page, /place\.sections\s*\n?\s*\.map\(/);
    assert.match(page, /place\.practical\.map\(\(p\) => `<tr><th scope="row">/);
  });

  test("each detail page embeds its OpenStreetMap viewbox with attribution", () => {
    assert.match(page, /place\.mapCenter/);
    assert.match(page, /place\.mapBounds/);
    assert.match(page, /place\.mapZoom/);
    assert.match(page, /https:\/\/www\.openstreetmap\.org\/export\/embed\.html/);
    assert.match(page, /loading="lazy"/);
    assert.match(page, /title="OpenStreetMap centered on \$\{place\.title\}/);
    assert.match(page, /openstreetmap\.org\/copyright/);
    assert.match(page, /OpenStreetMap contributors/);
  });

  test("highlights, experiences, and mindful guidance render from place data", () => {
    assert.match(page, /place\.highlights\.map\(card\)/);
    assert.match(page, /place\.experiences\.map\(card\)/);
    assert.match(page, /<p>\$\{place\.mindful\}<\/p>/);
  });

  test("seasons, festivals, and food each have their own block", () => {
    assert.match(page, /place\.seasons\s*\n?\s*\.map\(/);
    assert.match(page, /place\.festivals\s*\n?\s*\.map\(/);
    assert.match(page, /place\.food\.map\(\(f\) => `<li>/);
    assert.match(page, /tl-when.*f\.when/s);
  });

  test("next-place navigation cycles through all destinations", () => {
    assert.match(page, /const next = places\[\(index \+ 1\) % places\.length\]/);
    assert.match(page, /href="#\/\$\{next\.id\}">Next: \$\{next\.title\} →/);
  });

  test("hero parallax is transform-only and scroll-passive", () => {
    const parallax = MAIN.slice(
      MAIN.indexOf("function attachHeroParallax"),
      MAIN.indexOf("function attachReveals"),
    );
    assert.match(parallax, /translate3d\(0, \$\{y \* 0\.32\}px, 0\)/);
    assert.match(parallax, /\{ passive: true \}/);
  });

  test("hero parallax changes only transform and opacity", () => {
    const parallax = MAIN.slice(
      MAIN.indexOf("function attachHeroParallax"),
      MAIN.indexOf("function attachReveals"),
    );
    const changedProperties = [...parallax.matchAll(/\.style\.(\w+)\s*=/g)].map(
      (match) => match[1],
    );
    assert.deepEqual(new Set(changedProperties), new Set(["transform", "opacity"]));
    assert.match(parallax, /inner\.style\.opacity =/);
  });

  test("reveals target long-page blocks with a scroller-rooted observer", () => {
    const reveals = MAIN.slice(
      MAIN.indexOf("function attachReveals"),
      MAIN.indexOf("function showPage"),
    );
    assert.match(
      reveals,
      /\.prose, \.block, \.fact-strip, \.lede, \.mindful, \.place-card, \.place-nav/,
    );
    assert.match(reveals, /root: pageContent/);
    assert.match(reveals, /entry\.target\.classList\.add\("revealed"\)/);
  });

  test("content remains readable without an observer and with reduced motion", () => {
    const showPage = MAIN.slice(
      MAIN.indexOf("function showPage("),
      MAIN.indexOf("function route()"),
    );
    const reveals = MAIN.slice(
      MAIN.indexOf("function attachReveals"),
      MAIN.indexOf("function showPage"),
    );
    const reducedMotion = CSS.slice(CSS.lastIndexOf("@media (prefers-reduced-motion: reduce)"));

    // Content is inserted before observers are attached, and hidden reveal
    // classes are added only after the observer was successfully constructed.
    assert.ok(
      showPage.indexOf("pageContent.innerHTML = html;") < showPage.indexOf("attachReveals();"),
    );
    assert.ok(
      reveals.indexOf("new IntersectionObserver") < reveals.indexOf('classList.add("reveal")'),
    );
    assert.match(
      reducedMotion,
      /\.reveal\s*\{[^}]*opacity:\s*1;[^}]*transform:\s*none;[^}]*transition:\s*none;/s,
    );
  });
  test("place order makes the Jawai-to-Jaisalmer wrap concrete, per the spec example", () => {
    const placesSrc = fs.readFileSync(path.join(ROOT, "src", "data", "places.ts"), "utf8");
    const ids = [...placesSrc.matchAll(/^\s+id:\s*"([^"]+)"/gm)].map((m) => m[1]);
    assert.deepEqual(ids, ["jaisalmer", "jaipur", "udaipur", "jawai"]);
  });
});

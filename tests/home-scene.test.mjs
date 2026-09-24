/**
 * F2 — Home Scene (spec: docs/day3-specs/home-scene.md).
 *
 * Structural cases over src/three/HomeScene.ts: the poster-first guarantee, the
 * loading/ready/fallback state machine, and the animation-loop discipline that
 * keeps the landing cheap when it is not visible.
 */
import { test, describe } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const PUBLIC = path.join(ROOT, "public");
const SCENE = fs.readFileSync(path.join(ROOT, "src", "three", "HomeScene.ts"), "utf8");
const INDEX = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");

describe("home scene (F2)", () => {
  test("poster is in the DOM immediately with priority loading and real alt text", () => {
    assert.match(SCENE, /this\.poster = new Image\(\)/);
    assert.match(SCENE, /images\/home\/hawa-mahal\.webp/);
    assert.match(SCENE, /this\.poster\.fetchPriority = "high"/);
    assert.match(SCENE, /this\.poster\.alt =/);
    assert.match(SCENE, /Hawa Mahal in warm sandstone/);
    assert.match(SCENE, /container\.appendChild\(this\.poster\)/);
  });

  test("referenced poster and model files exist under public/", () => {
    assert.ok(fs.existsSync(path.join(PUBLIC, "images", "home", "hawa-mahal.webp")));
    assert.ok(fs.existsSync(path.join(PUBLIC, "models", "hawa_mahal_home.glb")));
  });

  test("home state machine covers loading, ready, and fallback", () => {
    assert.match(SCENE, /dataset\.homeState = "loading"/);
    assert.match(SCENE, /dataset\.homeState = "ready"/);
    assert.match(SCENE, /dataset\.homeState = "fallback"/);
  });

  test("model failure falls back to the still with a warning, never an empty hero", () => {
    assert.match(SCENE, /models\/hawa_mahal_home\.glb/);
    assert.match(SCENE, /Hawa Mahal is shown as a rendered still/);
    const failure = SCENE.slice(SCENE.indexOf("} catch (error) {"));
    assert.match(failure, /this\.container\.dataset\.homeState = "fallback"/);
    assert.match(failure, /console\.warn\(/);
    assert.match(failure, /this\.renderer\?\.setAnimationLoop\(null\)/);
  });

  test("WebGL context loss drops to fallback instead of freezing", () => {
    const lost = SCENE.slice(SCENE.indexOf('"webglcontextlost"'), SCENE.indexOf('"webglcontextrestored"'));
    assert.match(lost, /this\.container\.dataset\.homeState = "fallback"/);
    assert.match(lost, /this\.syncAnimation\(\)/);
    assert.match(SCENE, /webglcontextrestored/);
  });

  test("setActive hides the canvas accessibly and lazy-loads exactly once", () => {
    assert.match(SCENE, /this\.container\.style\.visibility = active \? "visible" : "hidden"/);
    assert.match(SCENE, /this\.container\.setAttribute\("aria-hidden", String\(!active\)\)/);
    assert.match(SCENE, /if \(active && !this\.started\) void this\.load\(\)/);
    const setActive = SCENE.slice(SCENE.indexOf("setActive(active: boolean)"), SCENE.indexOf("private syncAnimation"));
    assert.match(setActive, /this\.syncAnimation\(\)/);
  });

  test("reduced motion and hidden tabs stop the animation loop", () => {
    assert.match(SCENE, /prefers-reduced-motion: reduce/);
    assert.match(SCENE, /!document\.hidden && this\.ready/);
    assert.match(SCENE, /!this\.motion\.matches/);
    assert.match(SCENE, /this\.renderer\.setAnimationLoop\(animate \? this\.tick : null\)/);
  });

  test("paused rendering re-centres the eased view on the resting camera", () => {
    assert.match(SCENE, /if \(!animate\) this\.view = \{ yaw: REST_YAW, eye: REST_EYE \}/);
  });

  test("hero overlay links the Jaipur guide and the places grid", () => {
    assert.ok(INDEX.includes('href="#/jaipur"'), "landmark link to #/jaipur missing");
    assert.ok(INDEX.includes('href="#/places" id="home-cta"'), "Explore CTA missing");
    assert.ok(INDEX.includes('id="home-title"'), "home title missing");
    assert.ok(INDEX.includes('id="home-tagline"'), "home tagline missing");
    assert.ok(INDEX.includes('id="home-eyebrow">A JOURNEY THROUGH THE DESERT KINGDOM</div>'));
    assert.ok(INDEX.includes('id="home-title">RAJASTHAN</h1>'));
    assert.ok(INDEX.includes('id="home-tagline">Stories in sandstone. Cities in colour.</p>'));
    assert.ok(INDEX.includes('id="home-cta">Explore Destinations'));
  });

  test("poster append happens in the constructor, so first paint never waits on WebGL or the model", () => {
    const ctorStart = SCENE.indexOf("constructor(private container: HTMLElement)");
    const loadStart = SCENE.indexOf("private async load()");
    assert.ok(ctorStart !== -1 && loadStart !== -1 && ctorStart < loadStart);
    const ctorBody = SCENE.slice(ctorStart, loadStart);
    assert.match(ctorBody, /container.dataset.homeState = "loading"/);
    assert.match(ctorBody, /container\.appendChild\(this\.poster\)/);
  });

  test("WebGL renderer creation sits inside load()'s try block, so an unavailable WebGL context falls back like any other failure", () => {
    const loadStart = SCENE.indexOf("private async load()");
    const tryStart = SCENE.indexOf("try {", loadStart);
    const catchStart = SCENE.indexOf("} catch (error) {", loadStart);
    assert.ok(loadStart !== -1 && tryStart !== -1 && catchStart !== -1 && loadStart < tryStart && tryStart < catchStart);
    const tryBody = SCENE.slice(tryStart, catchStart);
    assert.match(tryBody, /new THREE\.WebGLRenderer\(/);
  });

  test("resize recomputes the facade-plane frame and repositions the poster to match", () => {
    const resize = SCENE.slice(SCENE.indexOf("private resize = ("), SCENE.indexOf("private render() {"));
    assert.match(resize, /this.frame = {/);
    assert.match(resize, /this.poster.style.width = /);
    assert.match(resize, /this.poster.style.left = /);
    assert.match(resize, /this.poster.style.top = /);
    assert.match(resize, /this\.renderer\?\.setSize\(width, height\)/);
    assert.ok(resize.includes("if (this.ready && this.active) this.render()"));
  });

  test("pointer easing is bounded to a small swing around the resting view, never a free-roam camera", () => {
    assert.ok(SCENE.includes("YAW_RANGE = THREE.MathUtils.degToRad(9)"));
    assert.ok(SCENE.includes("EYE_RANGE = 4.5"));
    const tick = SCENE.slice(SCENE.indexOf("private tick = "), SCENE.length);
    assert.ok(tick.includes("REST_YAW + this.pointer.x * YAW_RANGE"));
    assert.ok(tick.includes("REST_EYE - this.pointer.y * EYE_RANGE"));
  });

  test("the Jaipur landmark link names Hawa Mahal specifically, not a generic link", () => {
    assert.ok(INDEX.includes('class="home-landmark" href="#/jaipur"'), "landmark anchor missing expected class");
    assert.ok(INDEX.includes("Hawa Mahal"), "landmark link text should name Hawa Mahal");
  });

  test("model and poster URLs stay subpath-safe through BASE_URL", () => {
    assert.match(SCENE, /import\.meta\.env\.BASE_URL\}models\/hawa_mahal_home\.glb/);
    assert.match(SCENE, /import\.meta\.env\.BASE_URL\}images\/home\/hawa-mahal\.webp/);
  });
});

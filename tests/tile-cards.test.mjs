/**
 * F4 — Tile Cards 3D Runtime (spec: docs/day3-specs/tile-cards-3d.md).
 *
 * Structural cases over src/three/TileCard.ts: poster-first rendering, lazy
 * visibility-gated loops, the shared model cache, and clean teardown on route
 * changes. Four live WebGL contexts is the ceiling these cases protect.
 */
import { test, describe } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const TILE = fs.readFileSync(path.join(ROOT, "src", "three", "TileCard.ts"), "utf8");
const MAIN = fs.readFileSync(path.join(ROOT, "src", "main.ts"), "utf8");
const PLACES = fs.readFileSync(path.join(ROOT, "src", "data", "places.ts"), "utf8");

describe("tile cards 3D (F4)", () => {
  test("cards start on the poster and go live only after the first frame", () => {
    // The data-tile-state="poster" literal lives in the grid markup (F3); the
    // runtime itself flips dataset.tileState between "poster" and "live".
    assert.match(TILE, /this\.el\.dataset\.tileState = "poster"/);
    assert.match(TILE, /this\.el\.dataset\.tileState = "live"/);
  });

  test("the live state is assigned only after a frame has rendered", () => {
    const start = TILE.slice(TILE.indexOf("private async start()"), TILE.indexOf("private resize()"));
    assert.ok(start.indexOf("this.renderFrame();") < start.indexOf('this.el.dataset.tileState = "live"'));
  });

  test("model load failure keeps the poster with a warning", () => {
    assert.match(TILE, /\[tile\] could not load/);
  });

  test("missing WebGL keeps the poster instead of throwing", () => {
    assert.match(TILE, /\[tile\] WebGL unavailable, keeping poster/);
  });

  test("both model and WebGL failures explicitly restore poster state", () => {
    const start = TILE.slice(TILE.indexOf("private async start()"), TILE.indexOf("private resize()"));
    const loadFailure = start.slice(start.indexOf("catch (err) {"), start.indexOf("if (this.disposed) return;"));
    const rendererFailure = start.slice(start.indexOf("let renderer: THREE.WebGLRenderer"), start.indexOf("renderer.setPixelRatio"));
    assert.match(loadFailure, /console\.warn\(`\[tile\] could not load[\s\S]*?dataset\.tileState = "poster"/);
    assert.match(rendererFailure, /console\.warn\("\[tile\] WebGL unavailable, keeping poster"[\s\S]*?canvas\.remove\(\)[\s\S]*?dataset\.tileState = "poster"/);
  });

  test("models are cached per URL and cloned per card", () => {
    assert.match(TILE, /const modelCache = new Map<string, Promise<THREE\.Object3D>>/);
    assert.match(TILE, /scene\.clone\(true\)/);
  });

  test("loops are gated on visibility with a 200px pre-load margin", () => {
    assert.match(TILE, /rootMargin: "200px 0px"/);
    assert.match(TILE, /setVisible\(visible: boolean\) \{[^}]*void this\.start\(\);[^}]*this\.play\(\);/s);
  });

  test("leaving view pauses the loop and off-screen cards skip resize renders", () => {
    assert.match(TILE, /setVisible\(visible: boolean\) \{[^}]*\} else \{\s*this\.pause\(\);/s);
    assert.match(TILE, /refreshSize\(\) \{\s*if \(this\.visible && !document\.hidden\) this\.renderFrame\(\);\s*\}/);
    assert.match(TILE, /cancelAnimationFrame\(this\.raf\)/);
  });

  test("the observer uses the scroller as its root and observes every card", () => {
    assert.match(TILE, /new IntersectionObserver\([\s\S]*?\{ root: scrollRoot, rootMargin: "200px 0px"/);
    assert.match(TILE, /for \(const card of cards\) observer\.observe\(card\)/);
  });

  test("hover eases the spin rate instead of jumping it", () => {
    assert.match(TILE, /this\.targetSpin = this\.hovering \? 0\.34 : 0\.1/);
    assert.match(TILE, /this\.spin \+= \(this\.targetSpin - this\.spin\)/);
  });

  test("frame work is capped so four detailed scenes stay cheap", () => {
    assert.match(TILE, /1000 \/ 30/);
    assert.match(TILE, /Math\.min\(window\.devicePixelRatio, 1\.75\)/);
  });

  test("reduced motion renders one still frame, never a loop", () => {
    assert.match(TILE, /prefers-reduced-motion: reduce/);
    const play = TILE.slice(TILE.indexOf("private play()"), TILE.indexOf("private pause()"));
    const reducedBranch = play.slice(play.indexOf("if (reducedMotion.matches)"), play.indexOf("const loop = "));
    assert.match(reducedBranch, /if \(!this\.stillRendered\) \{[\s\S]*?this\.renderFrame\(\);[\s\S]*?this\.stillRendered = true;[\s\S]*?\}\s*return;/);
    assert.ok(!reducedBranch.includes("requestAnimationFrame"), "reduced motion must not schedule an animation loop");
  });

  test("unmount tears down observer, resize listener, and every renderer", () => {
    assert.match(TILE, /observer\?\.disconnect\(\)/);
    assert.match(TILE, /window\.removeEventListener\("resize", onResize\)/);
    assert.match(TILE, /for \(const tile of tiles\) tile\.dispose\(\)/);
    assert.match(TILE, /this\.renderer\?\.dispose\(\)/);
    assert.match(TILE, /this\.canvas\?\.remove\(\)/);
  });

  test("unmount clears module state before the next route mount", () => {
    const mount = TILE.slice(TILE.indexOf("export function mountTileCards"), TILE.indexOf("export function unmountTileCards"));
    const unmount = TILE.slice(TILE.indexOf("export function unmountTileCards"));
    assert.match(mount, /mountTileCards\(root: ParentNode, scrollRoot: Element \| null\) \{\s*unmountTileCards\(\);/);
    assert.match(unmount, /observer = undefined/);
    assert.match(unmount, /onResize = undefined/);
    assert.match(unmount, /tiles = \[\]/);
  });

  test("mount wires every [data-tile] card to its own model URL", () => {
    assert.match(TILE, /root\.querySelectorAll<HTMLElement>\("\[data-tile\]"\)/);
    assert.match(TILE, /url: el\.dataset\.tile!/);
  });

  test("the destination grid contributes at most four live tile contexts", () => {
    const grid = MAIN.slice(MAIN.indexOf("function placesGrid()"), MAIN.indexOf("function aboutPage()"));
    const destinationIds = [...PLACES.matchAll(/^\s+id: "[^"]+",?$/gm)];
    const tileMarkup = [...grid.matchAll(/data-tile=/g)];
    assert.equal(destinationIds.length, 4);
    assert.match(grid, /places\s*\n\s*\.map\(/);
    assert.equal(tileMarkup.length, 1, "one card template should create one tile per destination");
  });

  test("tiles share the isometric framing and lighting rig", () => {
    assert.match(TILE, /0\.5774/);
    assert.match(TILE, /lightTile\(renderer, scene, sphere\.radius\)/);
  });

  test("each tile's own bounds determine its camera and lighting scale", () => {
    assert.match(TILE, /new THREE\.Box3\(\)\.setFromObject\(model\)/);
    assert.match(TILE, /box\.getBoundingSphere\(new THREE\.Sphere\(\)\)/);
    assert.match(TILE, /const d = sphere\.radius \* 1\.2/);
    assert.match(TILE, /new THREE\.OrthographicCamera\(-d, d, d, -d, 0\.1, sphere\.radius \* 40\)/);
    assert.match(TILE, /lightTile\(renderer, scene, sphere\.radius\)/);
  });

  test("a load that resolves after the card scrolls away must not build a canvas or render (nothing renders for off-screen cards)", () => {
    const start = TILE.slice(TILE.indexOf("private async start()"), TILE.indexOf("private resize()"));
    const disposedGuardIndex = start.indexOf("if (this.disposed) return;");
    const canvasIndex = start.indexOf('const canvas = document.createElement("canvas");');
    assert.ok(
      disposedGuardIndex > -1 && canvasIndex > disposedGuardIndex,
      "expected a guard between the resolved model load and canvas creation",
    );
    const afterLoad = start.slice(disposedGuardIndex, canvasIndex);
    assert.match(
      afterLoad,
      /visible/,
      "a card that left the viewport while its model was still loading must not build a canvas/renderer or render a frame once the load resolves later — start() needs to re-check this.visible (not just this.disposed) before creating the canvas",
    );
  });

  test("reduced motion renders its still frame once, not again every time the card re-enters the viewport", () => {
    const play = TILE.slice(TILE.indexOf("private play()"), TILE.indexOf("private pause()"));
    const reducedBranchStart = play.indexOf("if (reducedMotion.matches)");
    const loopStart = play.indexOf("const loop = ");
    assert.ok(
      reducedBranchStart > -1 && loopStart > reducedBranchStart,
      "expected a reducedMotion.matches branch before the animation loop is defined",
    );
    const reducedBranch = play.slice(reducedBranchStart, loopStart);
    assert.match(
      reducedBranch,
      /if\s*\(!this\.\w+\)/,
      "setVisible(true) calls play() every time a card re-enters the viewport; under reduced motion this must render the still frame exactly once for the card's lifetime, not on every re-entry — guard the renderFrame() call with a one-shot flag (e.g. this.stillRendered)",
    );
  });
});

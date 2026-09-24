/**
 * F9 — Asset Delivery (spec: docs/day3-specs/asset-delivery.md).
 *
 * Runtime half of the delivery story: relative base plus BASE_URL-resolved
 * references, so the GitHub Pages subpath keeps working. The build half
 * (precompressed variants in dist/) is verified by the plugin proof listing in
 * docs/day3-results.md — a config file alone proves nothing.
 */
import { test, describe } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { places } from "../src/data/places.ts";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const MAIN = fs.readFileSync(path.join(ROOT, "src", "main.ts"), "utf8");
const SCENE = fs.readFileSync(path.join(ROOT, "src", "three", "HomeScene.ts"), "utf8");
const TILE = fs.readFileSync(path.join(ROOT, "src", "three", "TileCard.ts"), "utf8");
const VITE = fs.readFileSync(path.join(ROOT, "vite.config.ts"), "utf8");
const INDEX = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");
const DIST = path.join(ROOT, "dist");

function listFiles(directory) {
  if (!fs.existsSync(directory)) return [];
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const fullPath = path.join(directory, entry.name);
    return entry.isDirectory() ? listFiles(fullPath) : [fullPath];
  });
}

describe("asset delivery (F9)", () => {
  test("vite base is relative so subpath deploys work", () => {
    assert.match(VITE, /base:\s*"\.\/"/);
  });

  test("grid assets resolve through the BASE_URL helper", () => {
    assert.match(MAIN, /const asset = \(path: string\) => import\.meta\.env\.BASE_URL \+ path/);
    assert.match(MAIN, /data-tile="\$\{asset\(p\.tile\)\}"/);
    assert.match(MAIN, /src="\$\{asset\(p\.tilePoster\)\}"/);
    assert.match(MAIN, /src="\$\{asset\(place\.hero\)\}"/);
  });

  test("home model and poster resolve through BASE_URL", () => {
    assert.match(SCENE, /import\.meta\.env\.BASE_URL\}models\/hawa_mahal_home\.glb/);
    assert.match(SCENE, /import\.meta\.env\.BASE_URL\}images\/home\/hawa-mahal\.webp/);
  });

  test("no absolute /models or /images references in shipped sources", () => {
    for (const [name, src] of [
      ["main.ts", MAIN],
      ["HomeScene.ts", SCENE],
      ["TileCard.ts", TILE],
    ]) {
      assert.doesNotMatch(src, /"\/(models|images)\//, `${name} has an absolute asset URL`);
    }
  });

  test("all data-referenced asset paths stay relative", () => {
    for (const place of places) {
      for (const field of ["hero", "tile", "tilePoster"]) {
        assert.ok(!place[field].startsWith("/"), `${place.id}.${field} is absolute: ${place[field]}`);
      }
    }
  });

  test("favicon resolves through Vite's base URL and exists in public assets", () => {
    assert.match(INDEX, /rel="icon"[^>]*href="%BASE_URL%favicon\.svg"/);
    assert.ok(fs.existsSync(path.join(ROOT, "public", "favicon.svg")));
  });

  test(
    "production dist emits gzip (and configured Brotli) variants for every shipped asset class",
    { skip: !fs.existsSync(path.join(DIST, "index.html")) && "requires npm run build first" },
    () => {
      const outputFiles = listFiles(DIST);
      const extensions = [".glb", ".webp", ".png", ".js", ".css", ".html"];
      const brotliConfigured = /brotli|\.br/i.test(VITE);

      for (const extension of extensions) {
        const originals = outputFiles.filter((file) => path.extname(file).toLowerCase() === extension);
        assert.ok(originals.length > 0, `dist has no ${extension} outputs`);
        for (const original of originals) {
          const relative = path.relative(DIST, original);
          assert.ok(fs.existsSync(`${original}.gz`), `${relative} is missing its .gz variant`);
          if (brotliConfigured) {
            assert.ok(fs.existsSync(`${original}.br`), `${relative} is missing its configured .br variant`);
          }
        }
      }
    },
  );
});

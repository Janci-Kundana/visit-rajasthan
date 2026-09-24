# F6 — About Page

Owner: `place-page-builder` · Tests: `tests/about.test.mjs` · Source: `src/main.ts` (`aboutPage()`)

## What the feature does

The `#/about` page is the site colophon: what the guide covers, how the 3D is
put together, and credits. It is a short static page with no 3D runtime.

## Inputs

- `#/about` hash (routed by F1)

## What "correct" means

1. Renders inside the narrow page shell with kicker "Colophon" and heading
   "About Us".
2. Covers all four statements: scope (four destinations, no filler), landing
   construction (Blender Hawa Mahal + live Three.js + still fallback), grid
   construction (Blender isometric tiles + live models + still fallback),
   coverage list (Jaisalmer, Jaipur, Udaipur, Jawai Bandh), and credits
   (photography source, typefaces, Vite + TypeScript + Three.js).
3. Mounts no tile cards and starts no render loops.
4. Stays a colophon — it must not grow destination-style blocks (fact strips,
   seasons, practical tables) that belong on place pages.

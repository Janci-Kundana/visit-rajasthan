# F9 — Asset Delivery (base path + precompression)

Owner: `ux-accessibility-reviewer` · Tests: `tests/assets.test.mjs` + production `dist/` listing · Source: `vite.config.ts`, `src/main.ts` (`asset()`), `src/three/HomeScene.ts`, `src/three/TileCard.ts`

## What the feature does

The site ships ~36 MB of Blender models plus posters and photos, deployed under
a subpath (GitHub Pages). Two mechanisms keep that working: relative asset
resolution at runtime, and precompressed variants at build time so the server
can serve gzip/brotli instead of raw bytes.

## Inputs

- `vite.config.ts` (`base`, compression plugin)
- `import.meta.env.BASE_URL` at runtime
- Files under `public/` copied verbatim to `dist/`

## What "correct" means

1. `base` in `vite.config.ts` is relative (`"./"`) so built asset URLs work
   under any subpath.
2. Every runtime asset reference (the `asset()` helper, `data-tile` URLs, the
   HomeScene model and poster URLs) resolves through `import.meta.env.BASE_URL`
   — no absolute `/models/...` or `/images/...` references.
3. All data-referenced asset paths are relative (no leading `/`).
4. The favicon resolves through Vite's base URL and loads without a missing
   resource request on the production home page.
5. The production build emits `.gz` (and `.br` where configured) variants for
   `.glb`, `.webp`, `.png`, `.js`, `.css`, and `.html` outputs — check the
   `dist/` listing, not just the config file.
6. The compressed build still runs: the plugin proof screenshot loads the home
   page from the compressed `dist/` output with no console errors.

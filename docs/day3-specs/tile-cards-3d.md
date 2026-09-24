# F4 — Tile Cards 3D Runtime

Owner: `tilecard-keeper` · Tests: `tests/tile-cards.test.mjs` · Source: `src/three/TileCard.ts`

## What the feature does

Each `[data-tile]` card owns a small WebGL view of its Blender-built `.glb`
tile: model fetch starts on grid mount (and is warmed from home during idle
time or CTA hover), renderer creation and the slow turntable spin stay
visibility-gated, spin quickens on hover, models share a cache, and teardown
happens on route change. At most four contexts exist, each only running while
its card is visible.

## Inputs

| Input                  | Meaning                                                        |
| ---------------------- | -------------------------------------------------------------- |
| `mountTileCards(root, scrollRoot)` | Wire every `[data-tile]` card; fetch all models up front; safe to re-call per route |
| `preloadTiles(urls)` | Warm the shared model cache with no rendering (idle prefetch, CTA hover intent) |
| Intersection events    | Card within 600 px of the scroller viewport → visible          |
| Hover                  | `pointerenter` / `pointerleave` raises / lowers target spin    |
| `prefers-reduced-motion` | Single still frame instead of a loop                         |
| Model / WebGL failure  | Missing `.glb`, decode error, or no WebGL context              |
| `unmountTileCards()`   | Route change — dispose everything                              |
| Window resize          | Refit each live card to its canvas                             |

## What "correct" means

1. Cards start on the poster (`data-tile-state="poster"`) and flip to `live`
   only after the first frame renders; load or WebGL failure keeps the poster
   with a console warning — never a blank card.
2. Models fetch once per URL (shared `modelCache`) and are cloned per card so
   transforms never leak between cards.
3. Fetch is decoupled from visibility: grid mount fetches every model (plus an
   idle/hover warm from home) so slow networks stream GLBs behind the posters;
   visibility starts renderer creation and the loop, leaving the viewport
   pauses the loop. Nothing renders for off-screen cards.
4. Spin idles slow and eases toward the hover rate rather than jumping; frame
   work is capped at 30 Hz.
5. Reduced motion renders exactly one frame and never starts a loop.
6. `unmountTileCards()` disconnects the observer, removes the resize listener,
   disposes each renderer and canvas, and resets state so re-mounting is clean.
7. Tiles are framed by their own bounding sphere with the shared isometric
   camera and shared `lightTile()` rig — matching the Blender preview stills.

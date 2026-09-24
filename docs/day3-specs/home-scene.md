# F2 — Home Scene (Hawa Mahal landing)

Owner: `home-scene-guardian` · Tests: `tests/home-scene.test.mjs` · Source: `src/three/HomeScene.ts`, `index.html`

## What the feature does

The landing page renders a live Three.js view of a Blender-modelled Hawa Mahal
(`public/models/hawa_mahal_home.glb`) over a shader sky, with a rendered still
as the instant poster and the permanent fallback. The pointer eases the camera
around a resting view; the hero copy and calls to action sit on top.

## Inputs

| Input                  | Meaning                                                        |
| ---------------------- | -------------------------------------------------------------- |
| `setActive(true)`      | Home route entered — show canvas, lazy-load model on first visit |
| `setActive(false)`     | Left home — hide canvas, stop the animation loop               |
| Pointer position       | Eases camera yaw (±9°) and eye height around the resting view  |
| `prefers-reduced-motion` | Disables the animation loop entirely                         |
| `document.hidden`      | Pauses rendering while the tab is hidden                       |
| WebGL / load failure   | Model, context, or renderer failure at any stage               |
| Resize                 | Recomputes the facade-plane frame and poster placement         |

## What "correct" means

1. The poster (`images/home/hawa-mahal.webp`, `fetchpriority="high"`, full
   descriptive `alt`) is in the DOM from construction — first paint never waits
   for WebGL or the 12 MB model.
2. `container.dataset.homeState` is always one of `loading` → `ready` |
   `fallback`; it is never stuck on `loading` after load settles.
3. Any failure (model 404, WebGL unavailable, context lost) leaves the poster
   visible with state `fallback` and logs a warning — the hero is never empty.
4. `setActive(false)` sets `visibility: hidden` + `aria-hidden="true"` and stops
   the loop; `setActive(true)` reverses it and lazy-loads once.
5. Reduced motion or a hidden tab stops the loop and re-centres the eased view
   on the resting camera.
6. The hero overlay content is exact: eyebrow, `RAJASTHAN` title, tagline, the
   Jaipur landmark link (`#/jaipur`), and the Explore CTA (`#/places`).
7. Model and poster URLs resolve through `import.meta.env.BASE_URL` (relative,
   subpath-safe); the referenced files exist under `public/`.

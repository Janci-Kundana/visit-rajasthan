# F8 — UX & Accessibility Plumbing

Owner: `ux-accessibility-reviewer` · Tests: `tests/ux.test.mjs` · Source: `src/main.ts`, `index.html`, `src/three/*`

## What the feature does

The cross-cutting behaviour that makes the 3D showcase usable: hidden panels
stay out of the keyboard path, decorative canvases stay out of the
accessibility tree, motion respects user preference, images load with the
right priority, and the loading screen always gets out of the way.

## Inputs

- Route changes (panel visibility), `prefers-reduced-motion`, `document.hidden`
- Keyboard (Tab) traversal, screen-reader tree inspection
- Slow networks (poster-before-model loading order)

## What "correct" means

1. `#home-hero` and `#page-content` are `inert` whenever hidden and non-`inert`
   when shown — focus can never enter a hidden panel.
2. Exactly one surface is visible at a time; `body.on-home` matches home
   visibility.
3. Decorative WebGL canvases are `aria-hidden`; the home poster and every tile
   poster carry meaningful `alt`; purely decorative arrows (`→`, `↗`) are
   `aria-hidden`.
4. Tile posters use `loading="lazy"`; the home poster uses
   `fetchpriority="high"`.
5. `prefers-reduced-motion` stops both the home loop (F2) and the tile loops
   (F4); a hidden tab renders nothing.
6. The loading screen dismisses on every route, including all fallbacks (F1).
7. The header nav marks exactly the active section (`home`, `places`, `about`)
   and none on place pages.

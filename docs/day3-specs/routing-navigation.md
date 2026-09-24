# F1 — Routing & Navigation

Owner: `routing-navigator` · Tests: `tests/routing.test.mjs` · Source: `src/main.ts` (`route()`), `index.html`

## What the feature does

The site is a hash router with no framework. `route()` reads `location.hash`
(stripping `#/`), shows exactly one surface, keeps the header nav state in sync,
and always dismisses the loading screen — including on broken or unknown URLs.

## Inputs

| Input              | Example                   | Meaning                                        |
| ------------------ | ------------------------- | ---------------------------------------------- |
| Empty hash         | `` (or `#/`)              | Home landing with the live 3D scene            |
| `places`           | `#/places`                | Places grid with four destination cards        |
| `about`            | `#/about`                 | About / colophon page                          |
| Known place id     | `#/jaipur` or `#/jaipur/` | Detail page for that destination               |
| Anything else      | `#/jodhpur`, `#/places/x` | Unknown route — must fall back, never go blank |
| `hashchange` event | back / forward buttons    | Re-runs `route()` for the new hash             |

## What "correct" means

1. Empty hash: `#home-hero` visible and not `inert`; `#page-content` hidden and
   `inert`; `body.on-home` set; nav highlights Home; `scene.setActive(true)`.
2. `places`: grid rendered with four cards; nav highlights Places; tile cards
   mounted with the content scroller as observer root; scene deactivated.
3. `about`: colophon rendered; nav highlights About; scene deactivated.
4. Known place id: detail page for that place; no nav item forced active
   (header shows no destination section); hero parallax attached; scene
   deactivated.
5. One trailing slash on a known route is ignored. Nested, malformed, unknown,
   or differently-cased hashes resolve to the places grid (same as `places`);
   never an empty
   `#page-content`, never both panels visible, never both panels `inert`.
6. Every transition calls `unmountTileCards()` first so no orphan render loops
   or observers survive a route change.
7. `dismissLoader()` runs on every branch, including fallbacks — the loading
   screen cannot trap the user on any URL.
8. All internal links use `#/` hashes; all asset URLs go through `asset()` so
   the deployed subpath keeps working.

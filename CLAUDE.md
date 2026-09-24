# Visit Rajasthan — Claude Code guide

Visual travel guide to four Rajasthan destinations (Jaisalmer, Jaipur, Udaipur,
Jawai Bandh). Live at <https://janci-kundana.github.io/visit-rajasthan/>. Product
behavior is defined in [SPEC.md](SPEC.md); read it before changing what a page
does.

## Stack

- **Vite 5 + TypeScript**, no UI framework. Pages are HTML template strings
  rendered into the DOM by `src/main.ts`.
- **Three.js** for the home scene and the 3D tile cards. Models are `.glb` files
  built by the Blender scripts in `scripts/blender/`.
- **Node's built-in test runner** (`node --test`) for all tests. No Jest/Vitest.
- **Prettier** for formatting (`.prettierrc`: double quotes, semicolons, 100
  columns, trailing commas). A hook runs it after every edit.
- **GitHub Actions → GitHub Pages** deploys every push to `main`
  (`.github/workflows/deploy.yml`).

## Page structure

Single-page app with hash routing. `src/router.ts` (`resolveRoute`) maps the hash
to a surface; `src/main.ts` (`route`) renders it.

| Hash                 | Page              | Rendered by                                          |
| -------------------- | ----------------- | ---------------------------------------------------- |
| empty, `#`, `#/`     | Home (3D scene)   | `index.html` `#home-hero` + `src/three/HomeScene.ts` |
| `#/places`           | Destination grid  | `placesGrid()` + `mountTileCards()`                  |
| `#/{place-id}`       | Destination guide | `placePage(place)`                                   |
| `#/about`            | About / colophon  | `aboutPage()`                                        |
| unknown or malformed | Destination grid  | fallback in `resolveRoute`                           |

Where things live:

- `src/data/places.ts` — the single source of truth for destination content
  (`Place` interface, `places` array, `getPlace()`). Grid cards, routes and
  next-place links are all derived from this array.
- `src/three/` — `HomeScene.ts` (home), `TileCard.ts` (grid cards), `city.ts`,
  `sky.ts`, `tileLighting.ts`.
- `public/` — runtime assets (see naming below).
- `tests/` — one `*.test.mjs` file per feature; specs in `docs/day3-specs/`.

## Naming conventions

- **Place ids**: lowercase, single word, no hyphens (`jaipur`, `jawai`). The id
  is the route key and the asset file prefix, so it must never change once
  published.
- **Asset files**, all keyed by place id:
  - hero photo `public/images/{id}.jpg`
  - tile model `public/models/{id}_tile.glb`
  - tile poster `public/images/tiles/{id}.png`
  - Blender builder `scripts/blender/{id}_tile.py`
- **TypeScript**: `camelCase` functions and variables, `PascalCase` classes,
  interfaces and types (`HomeScene`, `Place`, `RouteResolution`),
  `UPPER_SNAKE_CASE` module constants (`DISTANCE`, `WALLS`). Files that export a
  class are `PascalCase.ts`; others are `camelCase.ts`.
- **Page builders** are named after the page: `placesGrid()`, `placePage()`,
  `aboutPage()`.
- **CSS classes**: lowercase kebab-case (`.map-frame`, `.hero-credit`),
  prefixed by the section they style (`.home-*`, `.map-*`, `.hl-*`).
- **Tests**: `tests/{feature}.test.mjs`; feature specs:
  `docs/day3-specs/{feature}.md`.
- **Branches**: short, kebab-case, describe the change
  (`home-street-walls`, `day2-hooks-observability`).

## Never change without asking

These are human-owned. The `guard-locked-files` hook blocks edits to them, and
the list lives in `.claude/locked-files.json`. Do not work around the hook; ask
a teammate instead.

- `package.json`, `package-lock.json` — dependencies and scripts
- `tsconfig.json`, `vite.config.ts` — build and type configuration
- `.github/workflows/*.yml` — deployment
- `.claude/settings.json`, `.claude/locked-files.json` — hook configuration

Also ask before:

- Renaming or removing a place id (it breaks published links and asset paths).
- Replacing hero photos or changing image credits (rights must be checked).
- Adding or changing historical or travel facts without a source. Mark uncertain
  claims for human review; never invent detail.
- Editing generated files: `public/models/*.glb` and
  `public/images/tiles/*.png` come from `scripts/blender/`. Change the script
  and rebuild instead.
- Pushing straight to `main`. Work on a branch and merge through a PR.

## Rules for changes

- Keep `public/` paths relative and wrap them in `asset()` so the GitHub Pages
  base path works.
- Each place's map center must sit inside its bounds, which are ordered west,
  south, east, north. Keep the OpenStreetMap contributor link visible.
- Grid cards must still show their poster if WebGL or the model fails to load.
- To add a destination, follow
  [`.claude/skills/add-destination/SKILL.md`](.claude/skills/add-destination/SKILL.md).
- When behavior changes, update the matching spec in `docs/day3-specs/` and the
  row in [TEST_CASES.md](TEST_CASES.md) with the real input, expected and actual
  result.

## Checks before committing

```sh
npm test            # full suite; a hook also runs it after every git commit
npm run typecheck
npm run build       # needed before the dist/ checks in tests/assets.test.mjs
```

For Blender changes, also follow the render and browser steps in
[`scripts/blender/README.md`](scripts/blender/README.md).

## Open items

- No Figma design source exists yet. When the team adds one, record the file
  URL and put exported frames under `docs/design/`.

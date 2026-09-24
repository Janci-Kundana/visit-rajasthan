# F3 — Places Grid

Owner: `tilecard-keeper` · Tests: `tests/places-grid.test.mjs` · Source: `src/main.ts` (`placesGrid()`)

## What the feature does

The `#/places` page renders one card per destination from `places.ts`. Each card
links to its detail page, carries the place accent theme, shows the transparent
poster PNG immediately, and exposes its model URL via `data-tile` for the 3D
tile runtime (F4).

## Inputs

- `places` array from `src/data/places.ts` (four entries)
- `asset()` base-path resolver
- Card viewport visibility (handled by F4; the grid only provides the hooks)

## What "correct" means

1. Exactly one card per place, in `places` order, each linking to `#/{id}`.
2. Each card sets `--accent` / `--accent-deep` from the place data and
   `data-tile` to the resolved model URL with `data-tile-state="poster"`.
3. Each card contains a poster `<img>` with `loading="lazy"` and
   `alt="Isometric model of {title}'s landmarks"`, plus kicker, name, tagline,
   and a "Read the guide →" call to action.
4. No card is ever empty: poster is present before any model loads, and the
   card remains meaningful if WebGL never runs (F4 guarantees the live swap).
5. Card order, ids, and links stay consistent with `getPlace()` — every card
   target resolves to a real detail page, and every place has a card.

# F7 — Content Data (places.ts)

Owner: `content-librarian` · Tests: `tests/places.test.mjs` (existing) + `tests/place-content.test.mjs` (Day 3 depth) · Source: `src/data/places.ts`

## What the feature does

`places.ts` is the single source of truth for every destination. Routing (F1),
the grid (F3), and the detail pages (F5) all read from it, so a data gap shows
up as a broken page, a blank card, or a dead link.

## Inputs

- Editor changes to the `places` array and the `Place` interfaces
- Files on disk under `public/` that the data points at

## What "correct" means

1. Exactly the four ids the nav expects — `jaisalmer`, `jaipur`, `udaipur`,
   `jawai` — unique and stable (routing keys off them).
2. Every `hero` / `tile` / `tilePoster` path is relative (no leading `/`) and
   resolves to a real file under `public/`.
3. `accent` / `accentDeep` are six-digit hex colours; `heroFocus` is a valid
   CSS `object-position` (`center 44%` style).
4. Minimum depth per place: lede over 120 chars, 3+ stats, 1+ prose section
   with non-empty body, 1+ highlight, 1+ experience, 1+ season, 1+ festival
   with name + date + text, 1+ food item, 1+ practical row, non-empty mindful
   note, hero credit, subtitle, and tagline.
5. `getPlace()` returns the place for known ids and `undefined` — never throws
   — for unknown, empty, or missing ids.
6. Each place has OpenStreetMap center coordinates and bounds ordered west,
   south, east, north; its center is contained by those bounds and its zoom is
   within the supported 1–19 range.

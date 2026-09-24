# F5 — Place Detail Page

Owner: `place-page-builder` · Tests: `tests/place-page.test.mjs` (+ `tests/place-content.test.mjs` for data depth) · Source: `src/main.ts` (`placePage()`)

## What the feature does

Each destination renders a long-form guide: hero photograph with credit,
lede, fact strip, prose sections, highlights, experiences, seasonal guidance,
festival timeline, food list, practical table, OpenStreetMap viewbox,
mindful-traveller note, and prev/next navigation — all tinted by the place
accent.

## Inputs

- `place: Place` resolved by `getPlace(hash)` (F1 guarantees only known ids arrive)
- Scroll position inside `#page-content` (drives parallax + reveals)

## What "correct" means

1. All thirteen blocks render in order: hero → lede → fact strip → prose →
   highlights → experiences → seasons → festivals → food → practical → map →
   mindful note → prev/next nav. No block is silently skipped when its data is
   present.
2. Hero shows the place photo with `heroFocus` cropping, the `heroCredit`
   caption, a "← All destinations" crumb, kicker, title, and tagline.
3. The page element sets `--accent`, `--accent-deep`, and `--focus` from data.
4. "Next" links to the following place cyclically (Jawai wraps to Jaisalmer);
   "← All destinations" links to `#/places`.
5. Each place supplies an OpenStreetMap center and bounds; the iframe marker is
   inside its viewbox, loads lazily, and has a descriptive title. A map link and
   visible OpenStreetMap contributor attribution accompany it.
6. Hero parallax is transform/opacity only and never blocks reading; reveals
   add `.revealed` via `IntersectionObserver` rooted on the scroller.
7. Content stays fully readable with observers disabled or reduced motion on —
   effects are enhancement, never a gate.
8. Unknown ids never reach this template (F1 falls back to the grid), so the
   template may assume a complete `Place`.

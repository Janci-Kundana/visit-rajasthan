---
name: add-destination
description: Add or extend a Visit Rajasthan destination. Use when editing a destination's content, route, OpenStreetMap view, photos, or Blender tile and poster.
---

# Add a destination

Use this workflow for a new destination or a substantial destination-content
change. The app builds its grid, routes, and detail pages from the `places`
array, so completeness and asset consistency matter more than adding a card by
hand.

## Workflow

1. Read `SPEC.md`, `docs/day3-specs/content-data.md`,
   `docs/day3-specs/place-detail-page.md`, and the nearest entry in
   `src/data/places.ts`. Use an unused lowercase id that can remain the route
   key; ask the team for missing editorial decisions rather than inventing them.
2. Gather reliable sources for historical and practical claims. Preserve the
   source or research notes so a teammate can review them. Record photo
   provenance and permission in the asset's accompanying project documentation.
3. Add a complete `Place` entry in `src/data/places.ts`: titles, subtitle,
   tagline, hero and credit, tile model/poster, crop, colors, lede, stats,
   sections, highlights, experiences, seasons, festivals, food, practical
   details, mindful guidance, and map fields.
4. Set `mapCenter`, `mapBounds`, and `mapZoom` from the intended landmark.
   Bounds use west, south, east, north order and must contain the center. The
   page generates the OpenStreetMap iframe and link from these fields; retain
   the contributor attribution.
5. Add the hero under `public/images/` and the Blender outputs under
   `public/models/` and `public/images/tiles/`. Use
   [`scripts/blender/README.md`](../../../scripts/blender/README.md) and the
   existing `{id}_tile.py` builders as references. Add the id to the `CITIES`
   tuple in `scripts/blender/build_tiles.py` and create its matching
   `{id}_tile.py` builder. Keep the model and poster framing consistent.
6. Confirm the id resolves through `getPlace()`, the grid links to it, its
   detail page renders, and the next-place cycle includes it. Keep `asset`
   paths relative so Vite's base URL applies.
7. Add content, asset, map-bounds, and detail-page coverage. Update the relevant
   feature specs and `TEST_CASES.md` with the input, expected result, and actual
   result from the checks you ran.
8. Run `npm test`, `npm run typecheck`, and `npm run build`. Inspect the
   destination page in a browser at desktop and mobile widths; confirm the hero,
   poster fallback, map marker/viewbox, and no broken asset requests.

## Completion criteria

A destination is complete when its grid card, direct hash route, long-form
guide, accessible map and attribution, sourced content, credited hero, Blender
model, poster fallback, and next-place navigation work together, and the tests
and production build pass.

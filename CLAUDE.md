# Visit Rajasthan — Claude Code guide

This file records repository conventions from the current code. It does not
replace the team's product decisions; review [SPEC.md](SPEC.md) before changing
product behavior.

## Before changing a feature

- Read the matching feature spec in `docs/day3-specs/` and update it when the
  behavior changes.
- For a new destination, follow
  [`.claude/skills/add-destination/SKILL.md`](.claude/skills/add-destination/SKILL.md).
- Keep [TEST_CASES.md](TEST_CASES.md) and `docs/day3-results.md` aligned with
  tests that were actually run.

## Project invariants

- The app is a static Vite/TypeScript site. `src/main.ts` owns page templates;
  `src/router.ts` resolves hash routes; `src/data/places.ts` owns destination
  data.
- Keep place ids unique and stable. Grid links, detail routes, and cyclic
  next-place links derive from the `places` array.
- Runtime assets under `public/` use relative paths and the `asset()` helper so
  the Vite base path works on GitHub Pages.
- Each place's OpenStreetMap center must be inside its bounds. Bounds use west,
  south, east, north order. Keep the visible OpenStreetMap contributor link.
- Every grid card must retain its poster if WebGL or model loading fails. For
  Blender model workflow and source-scene details, read
  [`scripts/blender/README.md`](scripts/blender/README.md).
- Keep destination facts and media credits reviewable. Mark uncertain claims
  for human verification instead of filling gaps with invented detail.

## Checks

Use `npm test` for the full Node test suite, `npm run typecheck` for TypeScript,
and `npm run build` for the production output. For Blender changes, also follow
the render and browser steps in `scripts/blender/README.md`.

## External project state

- A GitHub Pages deployment API 404 means Pages is not enabled. Ask a repository
  admin to choose **Settings → Pages → Source: GitHub Actions** before rerunning
  the workflow; a push-capable account cannot make that setting change.
- The repository has no Figma source link yet. If the team has approved Figma
  designs, record the file URL and add exported frames under `docs/design/`.

# Day 3 — Subagents, specs, tests, and plugin proof

## Scope

The site has nine real features covered here (routing, the home scene, the places grid, tile runtime, place detail, about, place data, accessibility, and asset delivery). There is no login, booking, or contact flow in this project, so those were not added as fictional feature specs.

Each spec states the feature behavior, inputs, and acceptance criteria. Its owner is one of the project roles in [`.claude/agents/`](../.claude/agents/). Claude Code launched all six project agents and supplied initial test additions. Its second orchestration was interrupted by a permission-classifier error before all agents returned. Three spec-first Codex subagents completed the remaining coverage and review. The complete suite below was rerun after those changes.

## Feature results

| Feature                     | Spec                                                      | Test cases                                                                                             |           Result |
| --------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ---------------: |
| F1 — Routing and navigation | [routing-navigation.md](day3-specs/routing-navigation.md) | [routing.test.mjs](../tests/routing.test.mjs)                                                          | **23/23 passed** |
| F2 — Home scene             | [home-scene.md](day3-specs/home-scene.md)                 | [home-scene.test.mjs](../tests/home-scene.test.mjs)                                                    | **15/15 passed** |
| F3 — Places grid            | [places-grid.md](day3-specs/places-grid.md)               | [places-grid.test.mjs](../tests/places-grid.test.mjs)                                                  |   **6/6 passed** |
| F4 — Tile cards 3D runtime  | [tile-cards-3d.md](day3-specs/tile-cards-3d.md)           | [tile-cards.test.mjs](../tests/tile-cards.test.mjs)                                                    | **20/20 passed** |
| F5 — Place detail page      | [place-detail-page.md](day3-specs/place-detail-page.md)   | [place-page.test.mjs](../tests/place-page.test.mjs)                                                    | **14/14 passed** |
| F6 — About page             | [about-page.md](day3-specs/about-page.md)                 | [about.test.mjs](../tests/about.test.mjs)                                                              |   **8/8 passed** |
| F7 — Content data           | [content-data.md](day3-specs/content-data.md)             | [places.test.mjs](../tests/places.test.mjs), [place-content.test.mjs](../tests/place-content.test.mjs) | **16/16 passed** |
| F8 — UX and accessibility   | [ux-accessibility.md](day3-specs/ux-accessibility.md)     | [ux.test.mjs](../tests/ux.test.mjs)                                                                    | **14/14 passed** |
| F9 — Asset delivery         | [asset-delivery.md](day3-specs/asset-delivery.md)         | [assets.test.mjs](../tests/assets.test.mjs), production `dist/` checks                                 |   **7/7 passed** |

The feature lanes contain **123 passing cases**. The full `npm test -- --test-reporter=dot` run on 2026-09-24 also passed the 22 hook and subagent lifecycle cases: **145 passed, 0 failed, 0 skipped**.

F1 now exercises actual hash inputs through the route resolver, including bare hashes, every destination id, single trailing slashes, nested paths, case mismatches, and unknown ids. F5 checks for a lazy OpenStreetMap viewbox and visible attribution. F7 verifies each map center falls inside its configured bounds.

## Build and type checks

- `npm run build` — passed on 2026-09-24. TypeScript completed and the build emitted `.gz` and `.br` variants for the shipped `.glb`, `.webp`, `.png`, `.js`, `.css`, and `.html` files.
- `npm test -- --test-reporter=dot` — passed, 145/145.

Vite reports the minified JavaScript chunk at 650.06 kB, above its 500 kB advisory threshold. This does not fail the production build; code splitting remains a follow-up optimization.

## Playwright plugin proof

The Playwright Claude Code plugin was already installed and enabled, so the existing plugin was reused. Its Playwright MCP server reported version `1.64.0-alpha-1789764292000`. The capture used `browser_resize`, `browser_navigate`, `browser_wait_for`, `browser_snapshot`, `browser_console_messages`, and `browser_take_screenshot` against the production preview at `http://127.0.0.1:4173`.

The repeatable capture is in [`scripts/capture-day3-playwright-proof.mjs`](../scripts/capture-day3-playwright-proof.mjs).

Playwright found **0 console errors and 0 warnings**. The captured accessibility snapshot shows the site navigation, Hawa Mahal image description, home heading, and destination links.

The same browser session also verified the route hash and visible page heading for the places grid (`#/places`), Jaipur detail (`#/jaipur`), about page (`#/about`), and the unknown-route fallback (`#/unknown-place`). Each route showed its expected heading.

![Production home page captured with Playwright](day3-evidence/home-dist.png)

Screenshot file: [docs/day3-evidence/home-dist.png](day3-evidence/home-dist.png).

## GitHub Pages status (2026-09-24)

The deployment workflow is configured for GitHub Actions, but the Pages site is
not enabled yet. The Pages API returns 404, and the latest deploy run
[failed at `deploy-pages`](https://github.com/Janci-Kundana/visit-rajasthan/actions/runs/35840998353)
with “Ensure GitHub Pages has been enabled.” The authenticated repository
permissions allow pushes but not administration, so the repo owner/admin needs
to choose **Settings → Pages → Source: GitHub Actions**. Rerun the workflow
after that setting is in place.

## Design source status

No Figma file link or approved frame exports were found in the repo. The existing
browser capture documents the implementation only. See [SPEC.md](../SPEC.md)
for the team review items.

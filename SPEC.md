# Visit Rajasthan — Product Specification

This is the product contract for Visit Rajasthan. Every change to the site must
keep to it; a change that needs different behavior updates this file first,
through a reviewed PR. Detailed acceptance criteria for each feature are in
[`docs/day3-specs/`](docs/day3-specs/), and the test evidence is in
[TEST_CASES.md](TEST_CASES.md).

## Product summary

Visit Rajasthan is a visual travel guide to four destinations: Jaisalmer,
Jaipur, Udaipur, and Jawai Bandh. It helps tourists compare destinations and
plan a trip before booking. It is a guide only: there are no accounts,
bookings, payments, or contact forms.

## Visitor

**Who the visitor is:** a tourist planning a trip to Rajasthan, who wants to
choose which destinations to visit and know what to expect there.

## What the site must let the tourist do

1. See at a glance which destinations the guide covers (home, then grid).
2. Open any destination directly from the grid or from a shared `#/{place-id}`
   link.
3. Read enough to decide whether to go: history, highlights, experiences, best
   season, festivals, food and practical information.
4. See where the destination is, on an embedded map with a link to a larger one.
5. Move on to the next destination without going back to the grid.
6. Do all of the above without WebGL, with reduced motion, or with a keyboard.

## Pages

| Page              | Must contain                                                                                                                                     | Spec                                                         |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------ |
| Home              | The Hawa Mahal 3D scene with a still-image fallback, camera movement that follows the pointer, and links to Jaipur and the destination grid.     | [home-scene.md](docs/day3-specs/home-scene.md)               |
| Places            | One card per destination, each with an isometric poster and an optional live 3D model.                                                           | [places-grid.md](docs/day3-specs/places-grid.md)             |
| Destination guide | Hero image with credit, history, highlights, experiences, seasons, festivals, food, practical information, travel guidance, next/previous links. | [place-detail-page.md](docs/day3-specs/place-detail-page.md) |
| Location map      | Part of each guide: a lazy-loaded OpenStreetMap view centred on the landmark, a larger-map link, and contributor attribution.                    | [place-detail-page.md](docs/day3-specs/place-detail-page.md) |
| About             | Project colophon and credits.                                                                                                                    | [about-page.md](docs/day3-specs/about-page.md)               |

## Routes

| Hash                                     | Result                   |
| ---------------------------------------- | ------------------------ |
| Empty, `#`, or `#/`                      | Home                     |
| `#/places`                               | Destination grid         |
| `#/about`                                | About page               |
| `#/{place-id}`                           | That destination's guide |
| A single trailing slash on a known route | Same known route         |
| Unknown, nested, or malformed hash       | Destination grid         |

Destination ids are stable route keys: `jaisalmer`, `jaipur`, `udaipur`, and
`jawai`. An id must never change once published. Full rules:
[routing-navigation.md](docs/day3-specs/routing-navigation.md).

## Content and media rules

- `src/data/places.ts` is the only source of destination content.
- Each destination has complete content fields, a hero image and credit, a
  Blender tile model and poster, a unique accent colour, and a map centre,
  bounds and zoom.
- Map bounds are ordered west, south, east, north. The marker centre must fall
  inside them, and every map keeps the OpenStreetMap contributor attribution.
- A destination's title, guide, grid card, route, next destination and asset
  paths must agree. See [content-data.md](docs/day3-specs/content-data.md) and
  the [add-destination skill](.claude/skills/add-destination/SKILL.md).
- Historical and travel claims, image rights and credits are reviewed by a
  person before they ship. Uncertain claims are marked, never invented.

## Accessibility and resilience

- Only the active page is exposed; hidden pages are inert.
- Posters and descriptive image text stay available if WebGL or a model fails.
- Home and tile animation respect reduced motion and page visibility.
- Maps load lazily and have descriptive iframe titles.
- The loading screen dismisses on every route, including unknown hashes.

Full rules: [ux-accessibility.md](docs/day3-specs/ux-accessibility.md).

## Delivery

- The production build uses Vite with a relative base path and precompressed
  static assets ([asset-delivery.md](docs/day3-specs/asset-delivery.md)).
- `.github/workflows/deploy.yml` builds `dist/` and deploys to GitHub Pages on
  every push to `main`.
- Live site: <https://janci-kundana.github.io/visit-rajasthan/>.
- Changes reach `main` through a reviewed PR, with `npm test`,
  `npm run typecheck` and `npm run build` passing.

## Out of scope

Accounts and login, bookings, payments, and contact forms.

## Open decisions for the team

1. Decide which content has priority for tourists.
2. Review destination facts, practical details, image credits and usage rights.
3. Figma: no design file is linked yet. When one exists, add the file URL and
   the approved frame exports under `docs/design/`.

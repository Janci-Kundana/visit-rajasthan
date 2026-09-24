# Visit Rajasthan — Product Specification

**Status:** Team review draft, prepared from the current implementation on
2026-09-24. The code establishes what the product currently does; the team
still owns the goals, audience, factual sources, and priorities. Review the
open items below before treating this as an approved product contract.

## Product summary

Visit Rajasthan is a visual travel guide to four destinations: Jaisalmer,
Jaipur, Udaipur, and Jawai Bandh. Visitors can browse a 3D-led home page, scan
the destination cards, and open a long-form guide with practical details and an
OpenStreetMap viewbox. An About page explains the guide.

The inferred user need is to compare destinations and orient a trip before
booking. The repository contains no user research validating that need yet.

## Current user experience

| Surface           | Current behavior                                                                                                                              | Source                                                |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| Home              | Hawa Mahal 3D scene, with a still image fallback, pointer camera movement, and links to Jaipur and the destination grid.                      | `index.html`, `src/three/HomeScene.ts`                |
| Places            | One card per `places` entry, with an isometric poster and optional live 3D model.                                                             | `src/main.ts` (`placesGrid`), `src/three/TileCard.ts` |
| Destination guide | Hero image, history, highlights, experiences, seasons, festivals, food, practical information, travel guidance, and next/previous navigation. | `src/main.ts` (`placePage`), `src/data/places.ts`     |
| Location map      | Lazy OpenStreetMap iframe centered on a destination landmark, with a larger-map link and contributor attribution.                             | `src/main.ts`, `src/data/places.ts`                   |
| About             | Project colophon and credits.                                                                                                                 | `src/main.ts` (`aboutPage`)                           |

## Supported routes

| Hash                                     | Result                   |
| ---------------------------------------- | ------------------------ |
| Empty, `#`, or `#/`                      | Home                     |
| `#/places`                               | Destination grid         |
| `#/about`                                | About page               |
| `#/{place-id}`                           | That destination's guide |
| A single trailing slash on a known route | Same known route         |
| Unknown, nested, or malformed hash       | Destination grid         |

Destination ids are stable route keys. The current ids are `jaisalmer`,
`jaipur`, `udaipur`, and `jawai`.

## Content and media requirements

- `src/data/places.ts` is the source of truth for destination content.
- Each destination needs complete content fields, a hero image and credit, a
  Blender tile model and poster, a unique accent, and map center/bounds/zoom.
- OpenStreetMap bounds are ordered west, south, east, north. The marker center
  must fall inside those bounds; every map must retain contributor attribution.
- A destination's title, guide, grid card, route, next destination, and asset
  paths must agree. See [the content data contract](docs/day3-specs/content-data.md)
  and [the add-destination skill](.claude/skills/add-destination/SKILL.md).
- Historical and travel claims, image rights, and credits need human review;
  the current content data does not hold a source citation for every claim.

## Accessibility and resilience

- Only the active route surface is exposed; a hidden surface is inert.
- Posters and descriptive image text remain available if WebGL or a model fails.
- Home and tile animation respect reduced-motion and visibility state.
- Destination maps load lazily and have descriptive iframe titles.
- The loading screen must dismiss for every route, including unknown hashes.

Detailed acceptance criteria are in the [F1–F9 feature specifications](docs/day3-specs/).

## Delivery

The production build uses Vite with a relative base path and precompressed
static assets. `.github/workflows/deploy.yml` builds `dist/` and deploys through
GitHub Pages. The repository's Pages API currently returns 404 and the latest
deployment [failed with “Ensure GitHub Pages has been enabled”](https://github.com/Janci-Kundana/visit-rajasthan/actions/runs/35840998353).
The workflow is ready, but the site is not live until a repository admin
enables Pages with **Source: GitHub Actions** and reruns deployment.

## Team review needed

1. Confirm the intended audience, the main decision this guide should support,
   and which content deserves priority. These goals are not stated in the code.
2. Review destination facts, practical details, image credits, and usage rights.
3. Confirm whether the team has Figma designs. No Figma file link or exported
   design frames are present in the repository. The existing
   [`home-dist.png`](docs/day3-evidence/home-dist.png) is a browser capture of
   the implementation, not a design source. If designs exist, add the file link
   and approved frame exports under `docs/design/`.
4. Confirm that authentication, bookings, payments, and contact forms are out
   of scope; none is implemented today.

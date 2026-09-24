import "./style.css";
import { HomeScene } from "./three/HomeScene";
import { mountTileCards, unmountTileCards } from "./three/TileCard";
import { places, getPlace, type Place } from "./data/places";
import { resolveRoute } from "./router";

const app = document.getElementById("app")!;
const loadingScreen = document.getElementById("loading-screen")!;
const loadingBarFill = document.getElementById("loading-bar-fill")!;
const primaryNav = document.getElementById("primary-nav")!;
const homeHero = document.getElementById("home-hero")!;
const pageContent = document.getElementById("page-content")!;

const scene = new HomeScene(app);

/** Resolves public assets against Vite's base, so the site works under a subpath. */
const asset = (path: string) => import.meta.env.BASE_URL + path;

function setActiveNav(route: string) {
  for (const link of primaryNav.querySelectorAll("a")) {
    link.classList.toggle("active", link.getAttribute("data-route") === route);
  }
}

function dismissLoader() {
  loadingBarFill.style.width = "100%";
  setTimeout(() => loadingScreen.classList.add("hidden"), 280);
}

function placesGrid() {
  return `
    <div class="page-shell">
      <header class="page-head">
        <p class="page-kicker">Destinations</p>
        <h2 class="page-heading">Places to Visit</h2>
        <p class="page-subheading">
          Four very different arguments for Rajasthan — a living fort in the Thar, a planned city
          painted rose, a lake capital that never surrendered, and a granite valley where leopards
          and herders share the same hills. Each one has a full guide: history, what to see, when to
          go, and how to get there.
        </p>
      </header>
      <div class="places-grid">
        ${places
          .map(
            (p, i) => `
            <a class="place-card is-tile" href="#/${p.id}" style="--accent:${p.accent};--accent-deep:${p.accentDeep}" data-reveal="${i}"
               data-tile="${asset(p.tile)}" data-accent="${p.accent}" data-tile-state="poster">
              <img class="place-card-poster" src="${asset(p.tilePoster)}" alt="Isometric model of ${p.title}'s landmarks" loading="lazy" />
              <div class="place-card-scrim"></div>
              <div class="place-card-body">
                <p class="place-card-kicker">${p.subtitle}</p>
                <h3 class="place-card-name">${p.title}</h3>
                <p class="place-card-tag">${p.tagline}</p>
                <span class="place-card-cta">Read the guide →</span>
              </div>
            </a>`,
          )
          .join("")}
      </div>
    </div>
  `;
}

function aboutPage() {
  return `
    <div class="page-shell narrow">
      <header class="page-head">
        <p class="page-kicker">Colophon</p>
        <h2 class="page-heading">About Us</h2>
      </header>
      <div class="about-content">
        <p>
          Visit Rajasthan is a small guide to four destinations in India's desert state, built for
          people deciding where to actually go rather than for people scrolling a listicle. Every
          destination page carries the history, the architecture, the practical logistics and the
          seasonal detail we wanted when we were planning our own trips — and none of the filler
          that usually pads travel writing out.
        </p>
        <h3>How it's put together</h3>
        <p>
          The landing page centres on a detailed Blender interpretation of Jaipur's Hawa Mahal.
          Projecting jharokha balconies, cusped arches, geometric lattice screens and carved
          sandstone trim are modelled in relief, with textured plaster and warm daylight.
          Three.js renders the façade live in your browser; a rendered still of the same model
          appears while it loads and remains available if the 3D view cannot run.
        </p>
        <p>
          The Places grid carries a second piece of 3D: each destination is an isometric tile
          modelled in Blender, showing the landmarks that make that city unmistakable — Hawa Mahal
          and the Samrat Yantra for Jaipur, the bastion ring of Sonar Quila for Jaisalmer, the Lake
          Palace afloat on Pichola for Udaipur, and granite koppies with a leopard on them for
          Jawai. The tiles load as real models and turn slowly in the card; if your browser can't
          run WebGL you get a rendered still of the same scene instead.
        </p>
        <p>
          The destination pages deliberately do the opposite. A 3D model is a poor way to
          communicate what a place feels like and a worse way to tell you when to visit, so those
          pages are photography and long-form text: a single large landscape image per destination
          and several thousand words of genuinely useful writing underneath it.
        </p>
        <h3>Coverage</h3>
        <p>
          Jaisalmer, Jaipur, Udaipur and Jawai Bandh. We'd rather cover four places properly than
          twenty badly — each guide is researched to the level of detail you'd expect from someone
          who has stayed there, not someone summarising a brochure.
        </p>
        <h3>Credits</h3>
        <p>
          Destination photography is sourced from Pinterest and used here for an academic project.
          Type is Cormorant Garamond and Inter. Built with Vite, TypeScript and Three.js.
        </p>
      </div>
    </div>
  `;
}

function placePage(place: Place) {
  const index = places.findIndex((p) => p.id === place.id);
  const next = places[(index + 1) % places.length];
  const { latitude, longitude } = place.mapCenter;
  const { west, south, east, north } = place.mapBounds;
  const mapParams = new URLSearchParams({
    bbox: `${west},${south},${east},${north}`,
    layer: "mapnik",
    marker: `${latitude},${longitude}`,
  });
  const mapEmbedUrl = `https://www.openstreetmap.org/export/embed.html?${mapParams}`;
  const mapLink = `https://www.openstreetmap.org/?mlat=${latitude}&mlon=${longitude}#map=${place.mapZoom}/${latitude}/${longitude}`;

  const card = (h: { name: string; meta: string; text: string }) => `
    <article class="hl-card">
      <h4>${h.name}</h4>
      <p class="hl-meta">${h.meta}</p>
      <p>${h.text}</p>
    </article>`;

  return `
    <article class="place" style="--accent:${place.accent};--accent-deep:${place.accentDeep};--focus:${place.heroFocus}">
      <div class="place-hero">
        <img class="place-hero-img" src="${asset(place.hero)}" alt="${place.heroCredit}" />
        <div class="place-hero-scrim"></div>
        <div class="place-hero-inner">
          <a class="crumb" href="#/places">← All destinations</a>
          <p class="place-kicker">${place.subtitle}</p>
          <h1 class="place-title">${place.title}</h1>
          <p class="place-tagline">${place.tagline}</p>
        </div>
        <p class="hero-credit">${place.heroCredit}</p>
      </div>

      <div class="place-body">
        <p class="lede">${place.lede}</p>

        <dl class="fact-strip">
          ${place.stats.map((s) => `<div><dt>${s.label}</dt><dd>${s.value}</dd></div>`).join("")}
        </dl>

        ${place.sections
          .map(
            (s) => `
            <section class="prose">
              <h2>${s.heading}</h2>
              ${s.body.map((p) => `<p>${p}</p>`).join("")}
            </section>`,
          )
          .join("")}

        <section class="block">
          <h2>What to see</h2>
          <div class="hl-grid">${place.highlights.map(card).join("")}</div>
        </section>

        <section class="block">
          <h2>Things to do</h2>
          <div class="hl-grid two">${place.experiences.map(card).join("")}</div>
        </section>

        <section class="block">
          <h2>When to go</h2>
          <div class="season-row">
            ${place.seasons
              .map(
                (s) => `
                <div class="season">
                  <p class="season-months">${s.months}</p>
                  <p class="season-label">${s.label}</p>
                  <p class="season-text">${s.text}</p>
                </div>`,
              )
              .join("")}
          </div>
        </section>

        <section class="block">
          <h2>Festivals &amp; the local calendar</h2>
          <ol class="timeline">
            ${place.festivals
              .map(
                (f) => `
                <li>
                  <p class="tl-when">${f.when}</p>
                  <h4>${f.name}</h4>
                  <p>${f.text}</p>
                </li>`,
              )
              .join("")}
          </ol>
        </section>

        <section class="block">
          <h2>What to eat</h2>
          <ul class="food-list">${place.food.map((f) => `<li>${f}</li>`).join("")}</ul>
        </section>

        <section class="block">
          <h2>Know before you go</h2>
          <table class="practical">
            <tbody>
              ${place.practical.map((p) => `<tr><th scope="row">${p.label}</th><td>${p.value}</td></tr>`).join("")}
            </tbody>
          </table>
        </section>

        <section class="block map-block" aria-labelledby="location-map-title">
          <div class="map-heading">
            <div>
              <p class="map-eyebrow">Explore with OpenStreetMap</p>
              <h2 id="location-map-title">Find ${place.title} on the map</h2>
            </div>
            <a class="map-link" href="${mapLink}" target="_blank" rel="noopener noreferrer">
              Open in OpenStreetMap <span aria-hidden="true">↗</span>
            </a>
          </div>
          <div class="map-frame">
            <iframe
              src="${mapEmbedUrl}"
              title="OpenStreetMap centered on ${place.title}, Rajasthan"
              loading="lazy"
              referrerpolicy="strict-origin-when-cross-origin"
              allowfullscreen
            ></iframe>
          </div>
          <p class="map-attribution">
            Map data © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap contributors</a>
          </p>
        </section>

        <aside class="mindful">
          <p class="mindful-label">Travel lightly</p>
          <p>${place.mindful}</p>
        </aside>

        <nav class="place-nav">
          <a href="#/places">← All destinations</a>
          <a class="next" href="#/${next.id}">Next: ${next.title} →</a>
        </nav>
      </div>
    </article>
  `;
}

/** Subtle parallax + fade on the destination hero while the content scrolls over it. */
function attachHeroParallax() {
  const hero = pageContent.querySelector<HTMLElement>(".place-hero");
  const img = pageContent.querySelector<HTMLElement>(".place-hero-img");
  const inner = pageContent.querySelector<HTMLElement>(".place-hero-inner");
  if (!hero || !img || !inner) return;

  const onScroll = () => {
    const y = pageContent.scrollTop;
    const t = Math.min(y / hero.offsetHeight, 1);
    img.style.transform = `translate3d(0, ${y * 0.32}px, 0) scale(${1 + t * 0.08})`;
    inner.style.transform = `translate3d(0, ${y * 0.16}px, 0)`;
    inner.style.opacity = `${1 - t * 1.15}`;
  };
  pageContent.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
}

/** Reveals blocks as they enter the viewport so long pages don't land all at once. */
function attachReveals() {
  const targets = pageContent.querySelectorAll<HTMLElement>(
    ".prose, .block, .fact-strip, .lede, .mindful, .place-card, .place-nav",
  );
  const io = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add("revealed");
          io.unobserve(entry.target);
        }
      }
    },
    { root: pageContent, rootMargin: "0px 0px -8% 0px", threshold: 0.05 },
  );
  for (const t of targets) {
    t.classList.add("reveal");
    io.observe(t);
  }
}

function showPage(html: string) {
  unmountTileCards();
  pageContent.innerHTML = html;
  pageContent.inert = false;
  pageContent.classList.remove("hidden");
  pageContent.scrollTop = 0;
  attachReveals();
}

function route() {
  const resolution = resolveRoute(
    window.location.hash,
    places.map((place) => place.id),
  );

  homeHero.classList.add("hidden");
  pageContent.classList.add("hidden");
  homeHero.inert = true;
  pageContent.inert = true;
  document.body.classList.toggle("on-home", resolution.type === "home");

  if (resolution.type === "home") {
    unmountTileCards();
    setActiveNav("home");
    scene.setActive(true);
    homeHero.classList.remove("hidden");
    homeHero.inert = false;
    dismissLoader();
    return;
  }

  scene.setActive(false);

  if (resolution.type === "about") {
    setActiveNav("about");
    showPage(aboutPage());
    dismissLoader();
    return;
  }

  if (resolution.type === "place") {
    const place = getPlace(resolution.id);
    if (place) {
      setActiveNav("");
      showPage(placePage(place));
      attachHeroParallax();
      dismissLoader();
      return;
    }
  }

  setActiveNav("places");
  showPage(placesGrid());
  mountTileCards(pageContent, pageContent);
  dismissLoader();
}

window.addEventListener("hashchange", route);
route();

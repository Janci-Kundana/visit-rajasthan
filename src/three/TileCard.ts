/**
 * Live isometric destination tiles for the Places grid.
 *
 * Each card owns a small WebGL view of its Blender-built .glb. Four contexts is
 * comfortably inside every browser's limit, and each one only runs while its card
 * is on screen, so the grid costs nothing when scrolled past.
 *
 * Until a model arrives the card shows the transparent poster PNG rendered from
 * the same Blender scene, which is also what stays up if WebGL is unavailable.
 * Nothing here ever leaves the card in an empty state.
 */
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { MeshoptDecoder } from "three/examples/jsm/libs/meshopt_decoder.module.js";
import { lightTile } from "./tileLighting";

const loader = new GLTFLoader();
loader.setMeshoptDecoder(MeshoptDecoder);

/** One decoded tile, shared between every card that asks for the same URL. */
const modelCache = new Map<string, Promise<THREE.Object3D>>();

function loadTile(url: string): Promise<THREE.Object3D> {
  let pending = modelCache.get(url);
  if (!pending) {
    pending = loader.loadAsync(url).then((gltf) => gltf.scene);
    modelCache.set(url, pending);
  }
  // Each card needs its own transform, so hand out a clone rather than the
  // cached original — geometries and materials are still shared underneath.
  return pending.then((scene) => scene.clone(true));
}

/**
 * Warm the shared model cache for a list of tile URLs without building any
 * renderers. Fetch failures are swallowed here — Tile.start() still handles
 * them per card with the poster fallback.
 */
export function preloadTiles(urls: readonly string[]) {
  for (const url of urls) {
    void loadTile(url).catch(() => {});
  }
}

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

interface CardOptions {
  el: HTMLElement;
  url: string;
}

class Tile {
  private readonly el: HTMLElement;
  private readonly url: string;
  private disposeLighting?: () => void;
  private canvas?: HTMLCanvasElement;
  private renderer?: THREE.WebGLRenderer;
  private scene?: THREE.Scene;
  private camera?: THREE.OrthographicCamera;
  private pivot?: THREE.Group;
  private raf = 0;
  private visible = false;
  private started = false;
  private disposed = false;
  private hovering = false;
  private spin = 0;
  private targetSpin = 0;
  private lastTime = 0;
  private frameRadius = 1;
  private viewportWidth = 0;
  private viewportHeight = 0;
  private stillRendered = false;

  constructor({ el, url }: CardOptions) {
    this.el = el;
    this.url = url;
    el.addEventListener("pointerenter", this.onEnter);
    el.addEventListener("pointerleave", this.onLeave);
  }

  private onEnter = () => {
    this.hovering = true;
  };

  private onLeave = () => {
    this.hovering = false;
  };

  /** Called by the IntersectionObserver; starts the loop and the lazy load. */
  setVisible(visible: boolean) {
    this.visible = visible;
    if (visible && !document.hidden) {
      void this.start();
      this.play();
    } else {
      this.pause();
    }
  }

  handleDocumentVisibility() {
    if (document.hidden) {
      this.pause();
      return;
    }
    if (this.visible) {
      void this.start();
      this.play();
    }
  }

  private async start() {
    if (this.started || this.disposed) return;
    this.started = true;

    let model: THREE.Object3D;
    try {
      model = await loadTile(this.url);
    } catch (err) {
      // Poster stays up — a missing tile must not blank the card.
      console.warn(`[tile] could not load ${this.url}`, err);
      this.el.dataset.tileState = "poster";
      return;
    }
    if (this.disposed) return;
    if (!this.visible || document.hidden) {
      // A card can leave the viewport or its tab can be hidden while the GLB
      // is loading. Let the next visible transition retry with the cached model.
      this.started = false;
      return;
    }

    const canvas = document.createElement("canvas");
    canvas.className = "place-card-canvas";
    canvas.setAttribute("aria-hidden", "true");
    this.el.prepend(canvas);
    this.canvas = canvas;

    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    } catch (err) {
      console.warn("[tile] WebGL unavailable, keeping poster", err);
      canvas.remove();
      this.el.dataset.tileState = "poster";
      return;
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
    this.renderer = renderer;

    const scene = new THREE.Scene();
    this.scene = scene;

    const pivot = new THREE.Group();
    scene.add(pivot);
    this.pivot = pivot;

    // Recentre the tile on its own bounding box so it spins about its middle
    // rather than about whatever origin the exporter happened to leave.
    const box = new THREE.Box3().setFromObject(model);
    const centre = box.getCenter(new THREE.Vector3());
    const sphere = box.getBoundingSphere(new THREE.Sphere());
    model.position.sub(centre);
    pivot.add(model);

    model.traverse((o) => {
      const mesh = o as THREE.Mesh;
      if (!mesh.isMesh) return;
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
      // Water receives architecture shadows; subpixel ripples are excluded
      // from the shadow map.
      if (materials.every((material) => material.name.endsWith("_water"))) mesh.castShadow = false;
      for (const material of materials) {
        const pbr = material as THREE.MeshStandardMaterial;
        for (const map of [pbr.map, pbr.normalMap, pbr.roughnessMap]) {
          if (map) map.anisotropy = Math.min(4, renderer.capabilities.getMaxAnisotropy());
        }
      }
    });

    const d = sphere.radius * 1.2;
    this.frameRadius = d;
    const camera = new THREE.OrthographicCamera(-d, d, d, -d, 0.1, sphere.radius * 40);
    const r = sphere.radius * 6;
    // Classic 45°/35.26° isometric, the same framing as the Blender previews.
    camera.position.set(r * 0.5774, r * 0.5774, r * 0.5774);
    const framingOffset = sphere.radius * 0.12;
    camera.position.y -= framingOffset;
    camera.lookAt(0, -framingOffset, 0);
    this.camera = camera;

    this.disposeLighting = lightTile(renderer, scene, sphere.radius);

    this.resize();
    this.renderFrame();
    this.stillRendered = reducedMotion.matches;
    this.el.dataset.tileState = "live";
    if (this.visible && !document.hidden) this.play();
  }

  private resize() {
    if (!this.renderer || !this.canvas) return;
    const w = this.canvas.clientWidth;
    const h = this.canvas.clientHeight;
    if (w === 0 || h === 0) return;
    if (w === this.viewportWidth && h === this.viewportHeight) return;
    this.viewportWidth = w;
    this.viewportHeight = h;
    this.renderer.setSize(w, h, false);
    if (this.camera) {
      // Fit the tile's width and adjust vertical coverage to the visual area.
      const aspect = w / h;
      const base = this.frameRadius / aspect;
      this.camera.left = -base * aspect;
      this.camera.right = base * aspect;
      this.camera.top = base;
      this.camera.bottom = -base;
      this.camera.updateProjectionMatrix();
    }
  }

  refreshSize() {
    if (this.visible && !document.hidden) this.renderFrame();
  }

  private play() {
    if (this.raf || !this.renderer || this.disposed || !this.visible || document.hidden) return;
    this.lastTime = performance.now();
    if (reducedMotion.matches) {
      if (!this.stillRendered) {
        this.renderFrame();
        this.stillRendered = true;
      }
      return;
    }
    const loop = (now: number) => {
      if (!this.visible || document.hidden || this.disposed) {
        this.pause();
        return;
      }
      this.raf = requestAnimationFrame(loop);
      // Slow model rotation does not need to shade four detailed scenes at 60Hz.
      if (now - this.lastTime < 1000 / 30) return;
      const dt = Math.min((now - this.lastTime) / 1000, 0.05);
      this.lastTime = now;
      this.targetSpin = this.hovering ? 0.34 : 0.1;
      this.spin += (this.targetSpin - this.spin) * Math.min(dt * 3.2, 1);
      if (this.pivot) this.pivot.rotation.y += this.spin * dt;
      this.renderFrame();
    };
    this.raf = requestAnimationFrame(loop);
  }

  private pause() {
    if (this.raf) cancelAnimationFrame(this.raf);
    this.raf = 0;
  }

  private renderFrame() {
    if (!this.renderer || !this.scene || !this.camera) return;
    this.resize();
    this.renderer.render(this.scene, this.camera);
  }

  dispose() {
    this.disposed = true;
    this.pause();
    this.el.removeEventListener("pointerenter", this.onEnter);
    this.el.removeEventListener("pointerleave", this.onLeave);
    this.disposeLighting?.();
    // Geometries and materials are shared via the model cache, so only the
    // per-card GPU context is torn down here.
    this.renderer?.dispose();
    this.canvas?.remove();
    this.renderer = undefined;
    this.scene = undefined;
    this.canvas = undefined;
  }
}

let tiles: Tile[] = [];
let observer: IntersectionObserver | undefined;
let onResize: (() => void) | undefined;
let onVisibilityChange: (() => void) | undefined;

/**
 * Wires up every `[data-tile]` card inside `root`. Safe to call on each route
 * change; the previous set is disposed first.
 */
export function mountTileCards(root: ParentNode, scrollRoot: Element | null) {
  unmountTileCards();

  const cards = Array.from(root.querySelectorAll<HTMLElement>("[data-tile]"));
  if (cards.length === 0) return;

  tiles = cards.map(
    (el) =>
      new Tile({
        el,
        url: el.dataset.tile!,
      }),
  );

  const byElement = new Map(cards.map((el, i) => [el, tiles[i]]));

  // Fetch every tile model up front so slow networks stream the GLBs while
  // the posters are on screen. Renderer creation, first-frame rendering, and
  // animation stay visibility-gated in setVisible()/start().
  preloadTiles(cards.map((el) => el.dataset.tile!));

  observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        byElement.get(entry.target as HTMLElement)?.setVisible(entry.isIntersecting);
      }
    },
    { root: scrollRoot, rootMargin: "600px 0px", threshold: 0.01 },
  );
  for (const card of cards) observer.observe(card);

  onResize = () => {
    for (const tile of tiles) tile.refreshSize();
  };
  window.addEventListener("resize", onResize, { passive: true });

  onVisibilityChange = () => {
    for (const tile of tiles) tile.handleDocumentVisibility();
  };
  document.addEventListener("visibilitychange", onVisibilityChange);
}

export function unmountTileCards() {
  observer?.disconnect();
  observer = undefined;
  if (onResize) window.removeEventListener("resize", onResize);
  onResize = undefined;
  if (onVisibilityChange) document.removeEventListener("visibilitychange", onVisibilityChange);
  onVisibilityChange = undefined;
  for (const tile of tiles) tile.dispose();
  tiles = [];
}

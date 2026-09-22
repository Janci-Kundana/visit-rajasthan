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

const loader = new GLTFLoader();

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

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

interface CardOptions {
  el: HTMLElement;
  url: string;
  accent: string;
}

class Tile {
  private readonly el: HTMLElement;
  private readonly url: string;
  private readonly accent: THREE.Color;
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

  constructor({ el, url, accent }: CardOptions) {
    this.el = el;
    this.url = url;
    this.accent = new THREE.Color(accent);
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
    if (visible) {
      void this.start();
      this.play();
    } else {
      this.pause();
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

    const canvas = document.createElement("canvas");
    canvas.className = "place-card-canvas";
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
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.12;
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
    });

    const d = sphere.radius * 1.12;
    const camera = new THREE.OrthographicCamera(-d, d, d, -d, 0.1, sphere.radius * 40);
    const r = sphere.radius * 6;
    // Classic 45°/35.26° isometric, the same framing as the Blender previews.
    camera.position.set(r * 0.5774, r * 0.5774, r * 0.5774);
    camera.lookAt(0, 0, 0);
    this.camera = camera;

    scene.add(new THREE.HemisphereLight(0xffffff, 0x8fa6bd, 2.0));
    const key = new THREE.DirectionalLight(0xfff1dc, 2.5);
    key.position.set(sphere.radius * 1.1, sphere.radius * 2.0, sphere.radius * 1.3);
    key.castShadow = true;
    key.shadow.mapSize.set(1024, 1024);
    const s = sphere.radius * 1.35;
    key.shadow.camera.left = -s;
    key.shadow.camera.right = s;
    key.shadow.camera.top = s;
    key.shadow.camera.bottom = -s;
    key.shadow.camera.near = 0.1;
    key.shadow.camera.far = sphere.radius * 8;
    key.shadow.bias = -0.0012;
    key.shadow.normalBias = 0.02;
    scene.add(key);

    // Accent-tinted bounce light, so each tile picks up its destination's colour.
    const bounce = new THREE.DirectionalLight(this.accent.getHex(), 0.7);
    bounce.position.set(-sphere.radius * 1.5, sphere.radius * 0.6, -sphere.radius * 1.2);
    scene.add(bounce);

    this.resize();
    this.el.dataset.tileState = "live";
    if (this.visible) this.play();
  }

  private resize() {
    if (!this.renderer || !this.canvas) return;
    const w = this.el.clientWidth;
    const h = this.el.clientHeight;
    if (w === 0 || h === 0) return;
    this.renderer.setSize(w, h, false);
    if (this.camera) {
      // Keep the tile's scale constant and widen the frustum instead, so the
      // model never squashes when the card's aspect ratio changes.
      const aspect = w / h;
      const base = (this.camera.top - this.camera.bottom) / 2;
      this.camera.left = -base * aspect;
      this.camera.right = base * aspect;
      this.camera.updateProjectionMatrix();
    }
  }

  private play() {
    if (this.raf || !this.renderer || this.disposed) return;
    this.lastTime = performance.now();
    if (reducedMotion.matches) {
      this.renderFrame();
      return;
    }
    const loop = (now: number) => {
      this.raf = requestAnimationFrame(loop);
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
        accent: el.dataset.accent || "#ffffff",
      }),
  );

  const byElement = new Map(cards.map((el, i) => [el, tiles[i]]));
  observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        byElement.get(entry.target as HTMLElement)?.setVisible(entry.isIntersecting);
      }
    },
    { root: scrollRoot, rootMargin: "200px 0px", threshold: 0.01 },
  );
  for (const card of cards) observer.observe(card);

  onResize = () => {
    for (const tile of tiles) tile.setVisible(true);
  };
  window.addEventListener("resize", onResize, { passive: true });
}

export function unmountTileCards() {
  observer?.disconnect();
  observer = undefined;
  if (onResize) window.removeEventListener("resize", onResize);
  onResize = undefined;
  for (const tile of tiles) tile.dispose();
  tiles = [];
}

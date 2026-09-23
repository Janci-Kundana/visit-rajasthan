import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { MeshoptDecoder } from "three/examples/jsm/libs/meshopt_decoder.module.js";
import { lightTile } from "./tileLighting";

// Resting camera, shared with the Blender still (hawa_mahal_home.py): level, 80 m
// out on the axis through the facade's centre, with the lens shifted rather than
// tilted so the palace's verticals stay vertical.
const DISTANCE = 80;
const REST_EYE = 17.1;
const REST_YAW = Math.atan2(1.2, 58);
const NEAR = 1;
const FAR = 400;
/** How far the pointer swings the view: around the facade, and up or down. */
const YAW_RANGE = THREE.MathUtils.degToRad(9);
const EYE_RANGE = 4.5;
/** The still's extent on the facade plane, in scene units (LEFT, RIGHT, TOP there). */
const STILL = { left: -38, right: 38, top: 21 };

/** The Blender Hawa Mahal on its street; the pointer swings the view around it. */
export class HomeScene {
  private renderer?: THREE.WebGLRenderer;
  private skyMaterial?: THREE.ShaderMaterial;
  private scene = new THREE.Scene();
  /** Its projection is set by hand in render(), for the lens shift. */
  private camera = new THREE.PerspectiveCamera();
  private poster: HTMLImageElement;
  private active = false;
  private started = false;
  private ready = false;
  private lastFrame = 0;
  /** The slice of the facade plane the screen shows, in scene units. */
  private frame = { width: 46.5, height: 32, centerY: 13 };
  /** Eased camera pose; it chases the pointer rather than jumping to it. */
  private view = { yaw: REST_YAW, eye: REST_EYE };
  private pointer = new THREE.Vector2();
  private motion = window.matchMedia("(prefers-reduced-motion: reduce)");

  constructor(private container: HTMLElement) {
    container.classList.add("home-scene");
    container.dataset.homeState = "loading";
    this.poster = new Image();
    this.poster.src = `${import.meta.env.BASE_URL}images/home/hawa-mahal.webp`;
    this.poster.alt =
      "Hawa Mahal in warm sandstone, with stepped storeys, carved balconies and arched lattice windows.";
    this.poster.className = "home-model-poster";
    this.poster.fetchPriority = "high";
    container.appendChild(this.poster);
    window.addEventListener("resize", this.resize);
    window.addEventListener(
      "pointermove",
      (event) => {
        this.pointer.set(
          (event.clientX / window.innerWidth) * 2 - 1,
          (event.clientY / window.innerHeight) * 2 - 1,
        );
      },
      { passive: true },
    );
    // Drift back to the resting view when the pointer leaves, or a touch lifts.
    const recentre = () => this.pointer.set(0, 0);
    document.documentElement.addEventListener("pointerleave", recentre);
    window.addEventListener("blur", recentre);
    for (const type of ["pointerup", "pointercancel"] as const) {
      window.addEventListener(type, (event) => {
        if (event.pointerType !== "mouse") recentre();
      });
    }
    this.motion.addEventListener("change", this.syncAnimation);
    document.addEventListener("visibilitychange", this.syncAnimation);
    this.resize();
  }

  private async load() {
    this.started = true;
    try {
      const renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        powerPreference: "high-performance",
      });
      this.renderer = renderer;
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
      renderer.domElement.setAttribute("aria-hidden", "true");
      this.container.appendChild(renderer.domElement);
      lightTile(renderer, this.scene, 22);
      renderer.shadowMap.autoUpdate = false;
      renderer.shadowMap.needsUpdate = true;
      this.addSky();
      renderer.domElement.addEventListener("webglcontextlost", (event) => {
        event.preventDefault();
        this.ready = false;
        this.container.dataset.homeState = "fallback";
        this.syncAnimation();
      });
      renderer.domElement.addEventListener("webglcontextrestored", () => {
        this.ready = this.scene.getObjectByName("Hawa Mahal") !== undefined;
        renderer.shadowMap.needsUpdate = true;
        this.container.dataset.homeState = this.ready ? "ready" : "fallback";
        this.syncAnimation();
      });
      this.resize();
      const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
      const gltf = await loader.loadAsync(`${import.meta.env.BASE_URL}models/hawa_mahal_home.glb`);
      const palace = gltf.scene;
      palace.name = "Hawa Mahal";
      palace.traverse((object) => {
        if (!(object instanceof THREE.Mesh)) return;
        object.castShadow = true;
        object.receiveShadow = true;
        for (const material of Array.isArray(object.material)
          ? object.material
          : [object.material]) {
          if (!(material instanceof THREE.MeshStandardMaterial)) continue;
          for (const texture of [material.map, material.normalMap, material.roughnessMap]) {
            if (texture) texture.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
          }
        }
      });
      this.scene.add(palace);
      renderer.shadowMap.needsUpdate = true;
      this.ready = true;
      this.render();
      this.container.dataset.homeState = "ready";
      this.syncAnimation();
    } catch (error) {
      this.container.dataset.homeState = "fallback";
      this.renderer?.setAnimationLoop(null);
      console.warn(
        "Hawa Mahal is shown as a rendered still because its 3D view could not load.",
        error,
      );
    }
  }

  private addSky() {
    this.skyMaterial = new THREE.ShaderMaterial({
      depthWrite: false,
      depthTest: false,
      uniforms: {
        zenith: { value: new THREE.Color(0x043267) },
        horizon: { value: new THREE.Color(0x389fbe) },
        cloud: { value: new THREE.Color(0xe0edf1) },
        aspect: { value: window.innerWidth / window.innerHeight },
      },
      vertexShader: `varying vec2 vUv;
        void main() { vUv = uv; gl_Position = vec4(position.xy, 1., 1.); }`,
      fragmentShader: `varying vec2 vUv;
        uniform vec3 zenith, horizon, cloud;
        uniform float aspect;
        float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
        float noise(vec2 p) {
          vec2 i = floor(p), f = fract(p); f = f * f * (3. - 2. * f);
          return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
        }
        float fbm(vec2 p) {
          float v = 0., a = .5;
          for (int i = 0; i < 5; i++) { v += a * noise(p); p = p * 2.03 + 13.7; a *= .5; }
          return v;
        }
        void main() {
          vec2 p = vec2((vUv.x - .5) * aspect, vUv.y) * 3. + vec2(3.7, 1.);
          float warp = fbm(p * .7);
          float wisps = fbm(p * 1.5 + vec2(warp, warp) * .7);
          float cloudCover = smoothstep(.46, .76, wisps) * smoothstep(.05, .6, vUv.y) * .32;
          vec3 color = mix(horizon, zenith, pow(vUv.y, .7));
          gl_FragColor = vec4(mix(color, cloud, cloudCover), 1.);
          #include <colorspace_fragment>
        }`,
    });
    const sky = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.skyMaterial);
    sky.frustumCulled = false;
    sky.renderOrder = -100;
    this.scene.add(sky);
  }

  setActive(active: boolean) {
    this.active = active;
    this.container.style.visibility = active ? "visible" : "hidden";
    this.container.setAttribute("aria-hidden", String(!active));
    if (active && !this.started) void this.load();
    this.syncAnimation();
  }

  private syncAnimation = () => {
    if (!this.renderer) return;
    const visible = this.active && !document.hidden && this.ready;
    const animate = visible && !this.motion.matches;
    if (!animate) this.view = { yaw: REST_YAW, eye: REST_EYE };
    this.renderer.setAnimationLoop(animate ? this.tick : null);
    if (visible) this.render();
  };

  private resize = () => {
    const width = window.innerWidth,
      height = window.innerHeight;
    const mobile = width < 700 && height > width;
    const viewHeight = Math.max(mobile ? 30 : 34, ((mobile ? 27 : 46.5) * height) / width);
    const viewWidth = (viewHeight * width) / height;
    // Desktop sits the palace high enough to leave the footway and road in view.
    this.frame = {
      width: viewWidth,
      height: viewHeight,
      centerY: viewHeight * (mobile ? 0.29 : 0.36),
    };
    // The still was rendered from the resting camera, so it only needs scaling and
    // placing: one scene unit on the facade plane is width / viewWidth pixels.
    const scale = width / viewWidth;
    this.poster.style.width = `${(STILL.right - STILL.left) * scale}px`;
    this.poster.style.left = `${width / 2 + STILL.left * scale}px`;
    this.poster.style.top = `${height / 2 - (STILL.top - this.frame.centerY) * scale}px`;
    this.renderer?.setSize(width, height);
    if (this.skyMaterial) this.skyMaterial.uniforms.aspect.value = width / height;
    if (this.ready && this.active) this.render();
  };

  private render() {
    const { yaw, eye } = this.view;
    const { width, height, centerY } = this.frame;
    // Orbit the vertical axis through the facade's centre, always looking level.
    this.camera.position.set(Math.sin(yaw) * DISTANCE, eye, Math.cos(yaw) * DISTANCE);
    this.camera.rotation.set(0, yaw, 0);
    // Lens shift: show the same slice of the facade plane at any eye height, so the
    // palace holds still on screen while the street and walls move around it.
    const k = NEAR / DISTANCE;
    const middle = centerY - eye;
    this.camera.projectionMatrix.makePerspective(
      (-width / 2) * k,
      (width / 2) * k,
      (middle + height / 2) * k,
      (middle - height / 2) * k,
      NEAR,
      FAR,
    );
    this.camera.projectionMatrixInverse.copy(this.camera.projectionMatrix).invert();
    this.renderer?.render(this.scene, this.camera);
  }

  private tick = (time: number) => {
    const dt = Math.min((time - this.lastFrame) / 1000, 0.1);
    this.lastFrame = time;
    const yaw = REST_YAW + this.pointer.x * YAW_RANGE - this.view.yaw;
    const eye = REST_EYE - this.pointer.y * EYE_RANGE - this.view.eye;
    // Settled on the pointer: nothing has changed, so don't redraw.
    if (Math.abs(yaw) < 1e-5 && Math.abs(eye) < 1e-4) return;
    // Ease towards the pointer so the view glides after it instead of tracking it.
    const ease = 1 - Math.exp(-dt * 4);
    this.view.yaw += yaw * ease;
    this.view.eye += eye * ease;
    this.render();
  };
}

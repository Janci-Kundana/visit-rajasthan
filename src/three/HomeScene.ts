import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { MeshoptDecoder } from "three/examples/jsm/libs/meshopt_decoder.module.js";
import { lightTile } from "./tileLighting";

/** The reference-inspired Blender facade, framed frontally at every screen size. */
export class HomeScene {
  private renderer?: THREE.WebGLRenderer;
  private skyMaterial?: THREE.ShaderMaterial;
  private scene = new THREE.Scene();
  private camera = new THREE.OrthographicCamera(-24, 24, 16, -16, 0.1, 200);
  private poster: HTMLImageElement;
  private active = false;
  private started = false;
  private ready = false;
  private lastFrame = 0;
  private renderedPointer = Number.NaN;
  private centerY = 13;
  private pointer = new THREE.Vector2();
  private motion = window.matchMedia("(prefers-reduced-motion: reduce)");

  constructor(private container: HTMLElement) {
    container.classList.add("home-scene");
    container.dataset.homeState = "loading";
    this.poster = new Image();
    this.poster.src = `${import.meta.env.BASE_URL}images/home/hawa-mahal.png`;
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
    this.renderer.setAnimationLoop(visible && !this.motion.matches ? this.tick : null);
    if (visible) this.render();
  };

  private resize = () => {
    const width = window.innerWidth,
      height = window.innerHeight;
    const mobile = width < 700 && height > width;
    const viewHeight = Math.max(mobile ? 30 : 32, ((mobile ? 27 : 46.5) * height) / width);
    const viewWidth = (viewHeight * width) / height;
    this.centerY = viewHeight * (mobile ? 0.29 : 0.405);
    Object.assign(this.camera, {
      left: -viewWidth / 2,
      right: viewWidth / 2,
      top: viewHeight / 2,
      bottom: -viewHeight / 2,
    });
    this.camera.updateProjectionMatrix();
    const posterWidth = (width * 46.5) / viewWidth;
    this.poster.style.width = `${posterWidth}px`;
    this.poster.style.left = `${(width - posterWidth) / 2}px`;
    this.poster.style.top = `${height * (0.5 + (this.centerY - 9.5) / viewHeight) - (posterWidth * 960) / 1800 / 2}px`;
    this.renderer?.setSize(width, height);
    if (this.skyMaterial) this.skyMaterial.uniforms.aspect.value = width / height;
    if (this.ready && this.active) this.render();
  };

  private render() {
    const parallax = this.motion.matches ? 0 : this.pointer.x * 0.8;
    this.camera.position.set(1.2 + parallax, this.centerY + 5.5, 58);
    this.camera.lookAt(0, this.centerY, 0);
    this.renderer?.render(this.scene, this.camera);
    this.renderedPointer = this.pointer.x;
  }

  private tick = (time: number) => {
    if (time - this.lastFrame < 1000 / 30) return;
    this.lastFrame = time;
    // The only moving part is pointer parallax; don't redraw a stationary view.
    if (this.renderedPointer === this.pointer.x) return;
    this.render();
  };
}

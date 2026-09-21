import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { createSky, type SkyPhase, skyPhases } from "./sky";
import { buildCity } from "./city";

const grainShader = {
  uniforms: {
    tDiffuse: { value: null as THREE.Texture | null },
    uTime: { value: 0 },
    uVignette: { value: 0.42 },
    uGrain: { value: 0.022 },
    uSaturation: { value: 1.24 },
  },
  vertexShader: /* glsl */ `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: /* glsl */ `
    uniform sampler2D tDiffuse;
    uniform float uTime;
    uniform float uVignette;
    uniform float uGrain;
    uniform float uSaturation;
    varying vec2 vUv;
    float rand(vec2 co) { return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453); }
    void main() {
      vec4 color = texture2D(tDiffuse, vUv);
      float luma = dot(color.rgb, vec3(0.2126, 0.7152, 0.0722));
      color.rgb = mix(vec3(luma), color.rgb, uSaturation);
      vec2 uv = vUv - 0.5;
      color.rgb *= 1.0 - dot(uv, uv) * uVignette;
      color.rgb += (rand(vUv * (uTime + 1.0)) - 0.5) * uGrain;
      gl_FragColor = color;
    }
  `,
};

/**
 * The landing-page animation: a procedurally generated, saturated Rajasthani
 * skyline on a lake, under a sky that cycles dawn → day → dusk → night.
 */
export class HomeScene {
  private renderer: THREE.WebGLRenderer;
  private scene = new THREE.Scene();
  private camera: THREE.PerspectiveCamera;
  private clock = new THREE.Clock();
  private composer: EffectComposer;
  private grainPass: ShaderPass;

  private sky: ReturnType<typeof createSky>;
  private city: ReturnType<typeof buildCity>;

  private hemi: THREE.HemisphereLight;
  private sun: THREE.DirectionalLight;
  private rim: THREE.DirectionalLight;
  private fill: THREE.DirectionalLight;

  private water: THREE.Mesh<THREE.CircleGeometry, THREE.ShaderMaterial>;
  private motes: THREE.Points<THREE.BufferGeometry, THREE.PointsMaterial>;
  private kites: THREE.Group;
  private stars: THREE.Points<THREE.BufferGeometry, THREE.PointsMaterial>;

  private elapsed = 0;
  private pointer = new THREE.Vector2();
  private pointerEased = new THREE.Vector2();
  private running = false;
  private phaseColor = {
    hemiSky: new THREE.Color(),
    hemiGround: new THREE.Color(),
    sun: new THREE.Color(),
    rim: new THREE.Color(),
    fill: new THREE.Color(),
  };

  constructor(container: HTMLElement) {
    this.renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.02;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(this.renderer.domElement);

    this.camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 400);
    this.camera.position.set(24, 11, 24);

    this.sky = createSky();
    this.scene.add(this.sky.mesh);

    this.city = buildCity();
    this.scene.add(this.city.group);

    this.water = this.createWater();
    this.scene.add(this.water);

    this.motes = this.createMotes();
    this.scene.add(this.motes);

    this.kites = this.createKites();
    this.scene.add(this.kites);

    this.stars = this.createStars();
    this.scene.add(this.stars);

    this.hemi = new THREE.HemisphereLight(0xffd9a8, 0x3a1f4d, 1.1);
    this.scene.add(this.hemi);

    this.sun = new THREE.DirectionalLight(0xfff0c9, 2.6);
    this.sun.position.set(22, 26, 12);
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.set(2048, 2048);
    this.sun.shadow.camera.left = -28;
    this.sun.shadow.camera.right = 28;
    this.sun.shadow.camera.top = 28;
    this.sun.shadow.camera.bottom = -28;
    this.sun.shadow.camera.far = 90;
    this.sun.shadow.bias = -0.0006;
    this.scene.add(this.sun);

    this.rim = new THREE.DirectionalLight(0xff4e8a, 1.5);
    this.rim.position.set(-18, 8, -16);
    this.scene.add(this.rim);

    this.fill = new THREE.DirectionalLight(0x4fd8ff, 0.9);
    this.fill.position.set(-8, 6, 20);
    this.scene.add(this.fill);

    this.composer = new EffectComposer(this.renderer);
    this.composer.addPass(new RenderPass(this.scene, this.camera));
    this.composer.addPass(new UnrealBloomPass(new THREE.Vector2(1, 1), 0.38, 0.6, 0.88));
    this.grainPass = new ShaderPass(grainShader);
    this.composer.addPass(this.grainPass);
    this.composer.addPass(new OutputPass());

    window.addEventListener("resize", () => this.resize());
    window.addEventListener("pointermove", (e) => {
      this.pointer.set((e.clientX / window.innerWidth) * 2 - 1, (e.clientY / window.innerHeight) * 2 - 1);
    });
    this.resize();
  }

  private createWater() {
    const geo = new THREE.CircleGeometry(105, 96);
    const mat = new THREE.ShaderMaterial({
      transparent: true,
      uniforms: {
        uTime: { value: 0 },
        uShallow: { value: new THREE.Color(0x2ec9c0) },
        uDeep: { value: new THREE.Color(0x11486e) },
        uSheen: { value: new THREE.Color(0xffd9a0) },
      },
      vertexShader: /* glsl */ `
        varying vec2 vUv;
        varying vec3 vPos;
        void main() {
          vUv = uv;
          vPos = position;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: /* glsl */ `
        uniform float uTime;
        uniform vec3 uShallow;
        uniform vec3 uDeep;
        uniform vec3 uSheen;
        varying vec2 vUv;
        varying vec3 vPos;
        void main() {
          float r = length(vPos.xy) / 105.0;
          float ripple = sin(vPos.x * 0.85 + uTime * 0.7)
                       + sin(vPos.y * 1.05 - uTime * 0.85)
                       + sin((vPos.x - vPos.y) * 0.5 + uTime * 0.4);
          vec3 col = mix(uShallow, uDeep, smoothstep(0.04, 0.6, r));
          // narrow specular streaks only, so the lake reads as water not pattern
          col += uSheen * smoothstep(2.25, 2.95, ripple) * 0.3 * (1.0 - smoothstep(0.1, 0.7, r));
          float edge = 1.0 - smoothstep(0.78, 1.0, r);
          gl_FragColor = vec4(col, 0.94 * edge);
        }
      `,
    });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.rotation.x = -Math.PI / 2;
    mesh.position.y = -0.22;
    mesh.receiveShadow = false;
    return mesh;
  }

  private createMotes() {
    const count = 1400;
    const pos = new Float32Array(count * 3);
    const col = new Float32Array(count * 3);
    const palette = [0xff4e8a, 0xffd166, 0x4fd8ff, 0x17b8a6, 0xf5a623, 0xffffff, 0xc86bff];
    const c = new THREE.Color();
    for (let i = 0; i < count; i++) {
      const a = Math.random() * Math.PI * 2;
      const r = 3 + Math.random() * 52;
      pos[i * 3] = Math.cos(a) * r;
      pos[i * 3 + 1] = Math.random() * 26 - 1;
      pos[i * 3 + 2] = Math.sin(a) * r;
      c.setHex(palette[(Math.random() * palette.length) | 0]);
      col[i * 3] = c.r;
      col[i * 3 + 1] = c.g;
      col[i * 3 + 2] = c.b;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    geo.setAttribute("color", new THREE.BufferAttribute(col, 3));
    const mat = new THREE.PointsMaterial({
      size: 0.17,
      vertexColors: true,
      transparent: true,
      opacity: 0.85,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      sizeAttenuation: true,
    });
    return new THREE.Points(geo, mat);
  }

  private createKites() {
    const group = new THREE.Group();
    const palette = [0xff4e8a, 0xffd166, 0x4fd8ff, 0x17b8a6, 0xf5a623, 0xc86bff, 0xe2573f, 0x1f9e5a];
    const shape = new THREE.Shape();
    shape.moveTo(0, 0.55);
    shape.lineTo(0.4, 0);
    shape.lineTo(0, -0.75);
    shape.lineTo(-0.4, 0);
    shape.closePath();
    const geo = new THREE.ShapeGeometry(shape);

    for (let i = 0; i < 16; i++) {
      const mat = new THREE.MeshStandardMaterial({
        color: palette[i % palette.length],
        emissive: palette[i % palette.length],
        emissiveIntensity: 0.28,
        side: THREE.DoubleSide,
        roughness: 0.55,
        metalness: 0,
      });
      const kite = new THREE.Mesh(geo, mat);
      const a = (i / 16) * Math.PI * 2 + Math.random() * 0.4;
      const r = 12 + Math.random() * 16;
      kite.position.set(Math.cos(a) * r, 9 + Math.random() * 11, Math.sin(a) * r);
      kite.scale.setScalar(0.9 + Math.random() * 0.9);
      kite.userData = { a, r, speed: 0.045 + Math.random() * 0.05, bob: Math.random() * Math.PI * 2 };

      const tailPts: THREE.Vector3[] = [];
      for (let t = 0; t < 7; t++) tailPts.push(new THREE.Vector3(0, -0.75 - t * 0.28, 0));
      const tail = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(tailPts),
        new THREE.LineBasicMaterial({ color: palette[(i + 3) % palette.length], transparent: true, opacity: 0.75 }),
      );
      kite.add(tail);
      group.add(kite);
    }
    return group;
  }

  private createStars() {
    const count = 900;
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const v = new THREE.Vector3().setFromSphericalCoords(
        150,
        Math.acos(Math.random() * 0.92),
        Math.random() * Math.PI * 2,
      );
      pos.set([v.x, v.y, v.z], i * 3);
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    const mat = new THREE.PointsMaterial({
      size: 0.9,
      color: 0xfff4e2,
      transparent: true,
      opacity: 0,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    return new THREE.Points(geo, mat);
  }

  private applyPhase(phase: SkyPhase, next: SkyPhase, t: number) {
    this.sky.apply(phase, next, t);

    this.phaseColor.hemiSky.setHex(phase.hemiSky).lerp(new THREE.Color(next.hemiSky), t);
    this.phaseColor.hemiGround.setHex(phase.hemiGround).lerp(new THREE.Color(next.hemiGround), t);
    this.phaseColor.sun.setHex(phase.sun).lerp(new THREE.Color(next.sun), t);
    this.phaseColor.rim.setHex(phase.rim).lerp(new THREE.Color(next.rim), t);
    this.phaseColor.fill.setHex(phase.fill).lerp(new THREE.Color(next.fill), t);

    this.hemi.color.copy(this.phaseColor.hemiSky);
    this.hemi.groundColor.copy(this.phaseColor.hemiGround);
    this.hemi.intensity = THREE.MathUtils.lerp(phase.hemiIntensity, next.hemiIntensity, t);

    this.sun.color.copy(this.phaseColor.sun);
    this.sun.intensity = THREE.MathUtils.lerp(phase.sunIntensity, next.sunIntensity, t);
    const sunAngle = THREE.MathUtils.lerp(phase.sunAngle, next.sunAngle, t);
    this.sun.position.set(Math.cos(sunAngle) * 30, Math.max(3, Math.sin(sunAngle) * 30), 14);

    this.rim.color.copy(this.phaseColor.rim);
    this.rim.intensity = THREE.MathUtils.lerp(phase.rimIntensity, next.rimIntensity, t);
    this.fill.color.copy(this.phaseColor.fill);

    const starOpacity = THREE.MathUtils.lerp(phase.stars, next.stars, t);
    this.stars.material.opacity = starOpacity;

    this.water.material.uniforms.uSheen.value.copy(this.phaseColor.sun);
  }

  setActive(active: boolean) {
    if (active === this.running) return;
    this.running = active;
    this.renderer.domElement.style.display = active ? "block" : "none";
    this.renderer.setAnimationLoop(active ? () => this.tick() : null);
  }

  private resize() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
    this.composer.setSize(w, h);
  }

  private tick() {
    const dt = Math.min(this.clock.getDelta(), 0.05);
    this.elapsed += dt;

    // Sky / light cycle: one full dawn→night loop every ~72 seconds.
    const cycle = (this.elapsed / 72) % 1;
    const scaled = cycle * skyPhases.length;
    const i = Math.floor(scaled);
    this.applyPhase(skyPhases[i], skyPhases[(i + 1) % skyPhases.length], scaled - i);

    // Camera: slow orbit, gentle rise and fall, plus eased pointer parallax.
    this.pointerEased.lerp(this.pointer, 0.04);
    // Opening pull-in from a high wide shot, then a permanent slow orbit.
    const intro = 1 - (1 - Math.min(this.elapsed / 4.2, 1)) ** 3;
    const dist = THREE.MathUtils.lerp(78, 47, intro) + Math.sin(this.elapsed * 0.11) * 3;
    const height = THREE.MathUtils.lerp(36, 15.5, intro) + Math.sin(this.elapsed * 0.17) * 2;
    const orbit = -0.6 + this.elapsed * 0.05;
    this.camera.position.set(
      Math.cos(orbit) * dist + this.pointerEased.x * 3.4,
      height - this.pointerEased.y * 3,
      Math.sin(orbit) * dist,
    );
    this.camera.lookAt(0, 4.6, 0);

    this.city.update(this.elapsed);

    this.water.material.uniforms.uTime.value = this.elapsed;

    const motePos = this.motes.geometry.getAttribute("position") as THREE.BufferAttribute;
    for (let m = 0; m < motePos.count; m++) {
      let y = motePos.getY(m) + dt * (0.35 + (m % 7) * 0.06);
      if (y > 25) y = -1;
      motePos.setY(m, y);
    }
    motePos.needsUpdate = true;
    this.motes.rotation.y = this.elapsed * 0.014;

    for (const kite of this.kites.children as THREE.Mesh[]) {
      const d = kite.userData as { a: number; r: number; speed: number; bob: number };
      d.a += dt * d.speed;
      kite.position.x = Math.cos(d.a) * d.r;
      kite.position.z = Math.sin(d.a) * d.r;
      kite.position.y += Math.sin(this.elapsed * 0.8 + d.bob) * dt * 0.7;
      kite.rotation.z = Math.sin(this.elapsed * 1.1 + d.bob) * 0.32;
      kite.rotation.y = -d.a + Math.PI / 2;
    }

    this.stars.rotation.y = this.elapsed * 0.006;
    this.grainPass.uniforms.uTime.value += dt;
    this.composer.render();
  }
}

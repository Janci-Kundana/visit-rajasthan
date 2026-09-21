import * as THREE from "three";

export interface SkyPhase {
  name: string;
  top: number;
  horizon: number;
  bottom: number;
  glow: number;
  /** Radians above the horizon, 0 = due east at eye level, PI/2 = overhead. */
  sunAngle: number;
  sunSize: number;
  hemiSky: number;
  hemiGround: number;
  hemiIntensity: number;
  sun: number;
  sunIntensity: number;
  rim: number;
  rimIntensity: number;
  fill: number;
  /** 0–1 star field opacity. */
  stars: number;
}

/** A full day in five saturated stops, looped by HomeScene. */
export const skyPhases: SkyPhase[] = [
  {
    name: "dawn",
    top: 0x3b2a7a,
    horizon: 0xff6b9d,
    bottom: 0xffb347,
    glow: 0xffd3a0,
    sunAngle: 0.12,
    sunSize: 0.055,
    hemiSky: 0xffb3c9,
    hemiGround: 0x3a1f4d,
    hemiIntensity: 1.0,
    sun: 0xffb37a,
    sunIntensity: 2.0,
    rim: 0xff4e8a,
    rimIntensity: 1.8,
    fill: 0x7a6bff,
    stars: 0.25,
  },
  {
    name: "morning",
    top: 0x1668c9,
    horizon: 0x6fe0e8,
    bottom: 0xfff0b8,
    glow: 0xffe4b0,
    sunAngle: 0.7,
    sunSize: 0.032,
    hemiSky: 0xcfefff,
    hemiGround: 0xc98a4a,
    hemiIntensity: 1.05,
    sun: 0xfff3d2,
    sunIntensity: 3.0,
    rim: 0x17b8a6,
    rimIntensity: 0.9,
    fill: 0x4fd8ff,
    stars: 0,
  },
  {
    name: "midday",
    top: 0x0a74cc,
    horizon: 0x2ec9b8,
    bottom: 0xffd98a,
    glow: 0xffe9b0,
    sunAngle: 1.32,
    sunSize: 0.028,
    hemiSky: 0xe4f7ff,
    hemiGround: 0xd8a35c,
    hemiIntensity: 1.1,
    sun: 0xffffff,
    sunIntensity: 3.2,
    rim: 0x2f8fd6,
    rimIntensity: 0.7,
    fill: 0x8ef0ff,
    stars: 0,
  },
  {
    name: "dusk",
    top: 0x4b1d7d,
    horizon: 0xff4e50,
    bottom: 0xffa552,
    glow: 0xffc27a,
    sunAngle: 0.22,
    sunSize: 0.062,
    hemiSky: 0xffa06b,
    hemiGround: 0x4b1d5a,
    hemiIntensity: 1.05,
    sun: 0xff9a5c,
    sunIntensity: 2.4,
    rim: 0xd6246e,
    rimIntensity: 2.1,
    fill: 0x6b7bff,
    stars: 0.35,
  },
  {
    name: "night",
    top: 0x070b2e,
    horizon: 0x5b2b8a,
    bottom: 0x1b3a6b,
    glow: 0x9ec8ff,
    sunAngle: 1.05,
    sunSize: 0.022,
    hemiSky: 0x6f7fd6,
    hemiGround: 0x120c28,
    hemiIntensity: 0.55,
    sun: 0xb9cdff,
    sunIntensity: 0.85,
    rim: 0xc86bff,
    rimIntensity: 1.4,
    fill: 0x3f6bd6,
    stars: 1,
  },
];

export function createSky() {
  const uniforms = {
    uTop: { value: new THREE.Color(skyPhases[0].top) },
    uHorizon: { value: new THREE.Color(skyPhases[0].horizon) },
    uBottom: { value: new THREE.Color(skyPhases[0].bottom) },
    uGlow: { value: new THREE.Color(skyPhases[0].glow) },
    uSunDir: { value: new THREE.Vector3(1, 0.2, 0.3).normalize() },
    uSunSize: { value: skyPhases[0].sunSize },
  };

  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(160, 48, 32),
    new THREE.ShaderMaterial({
      side: THREE.BackSide,
      depthWrite: false,
      uniforms,
      vertexShader: /* glsl */ `
        varying vec3 vDir;
        void main() {
          vDir = normalize((modelMatrix * vec4(position, 1.0)).xyz);
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: /* glsl */ `
        uniform vec3 uTop;
        uniform vec3 uHorizon;
        uniform vec3 uBottom;
        uniform vec3 uGlow;
        uniform vec3 uSunDir;
        uniform float uSunSize;
        varying vec3 vDir;
        void main() {
          vec3 d = normalize(vDir);
          float h = d.y;
          vec3 col = h > 0.0
            ? mix(uHorizon, uTop, pow(clamp(h, 0.0, 1.0), 0.62))
            : mix(uHorizon, uBottom, pow(clamp(-h, 0.0, 1.0), 0.55));

          // banded haze near the horizon, drifting slightly with direction
          col += uGlow * pow(1.0 - abs(h), 11.0) * 0.16;

          float sd = dot(d, normalize(uSunDir));
          col += uGlow * pow(clamp(sd, 0.0, 1.0), 48.0) * 0.34;
          col += vec3(1.0) * smoothstep(1.0 - uSunSize, 1.0 - uSunSize * 0.45, sd) * 1.1;

          gl_FragColor = vec4(col, 1.0);
        }
      `,
    }),
  );
  mesh.frustumCulled = false;

  const tmpA = new THREE.Color();
  const tmpB = new THREE.Color();
  const mix = (target: THREE.Color, a: number, b: number, t: number) => {
    tmpA.setHex(a);
    tmpB.setHex(b);
    target.copy(tmpA.lerp(tmpB, t));
  };

  function apply(phase: SkyPhase, next: SkyPhase, t: number) {
    mix(uniforms.uTop.value, phase.top, next.top, t);
    mix(uniforms.uHorizon.value, phase.horizon, next.horizon, t);
    mix(uniforms.uBottom.value, phase.bottom, next.bottom, t);
    mix(uniforms.uGlow.value, phase.glow, next.glow, t);
    uniforms.uSunSize.value = THREE.MathUtils.lerp(phase.sunSize, next.sunSize, t);
    const angle = THREE.MathUtils.lerp(phase.sunAngle, next.sunAngle, t);
    uniforms.uSunDir.value.set(Math.cos(angle), Math.sin(angle), 0.42).normalize();
  }

  return { mesh, apply };
}

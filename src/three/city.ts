import * as THREE from "three";

/** Deterministic RNG so the skyline is identical on every visit. */
function mulberry32(seed: number) {
  return () => {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const WALLS = [0xf7e7c8, 0xffd9b0, 0xf6c9a8, 0xfff4e2, 0xf3d9f0];
const PAINT = [0xe2573f, 0xd6246e, 0xf5a623, 0x17b8a6, 0x2f8fd6, 0x4433a8, 0x1f9e5a, 0xc86bff, 0xff4e8a];
const ROOFS = [0x17b8a6, 0x2f8fd6, 0xd6246e, 0x1f9e5a, 0xf5a623, 0x4433a8];
const GOLD = 0xffc93c;

const wallMat = (color: number) =>
  new THREE.MeshStandardMaterial({ color, roughness: 0.78, metalness: 0.02 });

const paintMat = (color: number) =>
  new THREE.MeshStandardMaterial({ color, roughness: 0.52, metalness: 0.06 });

const goldMat = () =>
  new THREE.MeshStandardMaterial({ color: GOLD, roughness: 0.28, metalness: 0.85, emissive: 0x3a2400 });

const windowMat = (color: number) =>
  new THREE.MeshStandardMaterial({
    color,
    emissive: color,
    emissiveIntensity: 0.9,
    roughness: 0.4,
    metalness: 0,
  });

function addDome(parent: THREE.Object3D, radius: number, y: number, color: number) {
  const dome = new THREE.Mesh(
    new THREE.SphereGeometry(radius, 20, 14, 0, Math.PI * 2, 0, Math.PI / 2),
    paintMat(color),
  );
  dome.position.y = y;
  parent.add(dome);

  const neck = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.22, radius * 0.3, radius * 0.5, 10), goldMat());
  neck.position.y = y + radius * 0.95;
  parent.add(neck);

  const finial = new THREE.Mesh(new THREE.ConeGeometry(radius * 0.17, radius * 0.62, 10), goldMat());
  finial.position.y = y + radius * 1.4;
  parent.add(finial);
  return dome;
}

function addChhatri(parent: THREE.Object3D, s: number, y: number, radius: number, color: number) {
  const g = new THREE.Group();
  g.position.y = y;

  const deck = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius * 1.1, 0.12 * s, 12), wallMat(0xfff4e2));
  g.add(deck);

  const pillarGeo = new THREE.CylinderGeometry(0.055 * s, 0.055 * s, 0.7 * s, 6);
  const pillarMat = wallMat(0xfff4e2);
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * Math.PI * 2;
    const p = new THREE.Mesh(pillarGeo, pillarMat);
    p.position.set(Math.cos(a) * radius * 0.78, 0.4 * s, Math.sin(a) * radius * 0.78);
    g.add(p);
  }

  const lintel = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.95, radius * 0.95, 0.1 * s, 12), wallMat(0xfff4e2));
  lintel.position.y = 0.78 * s;
  g.add(lintel);

  addDome(g, radius * 0.92, 0.82 * s, color);
  parent.add(g);
  return g;
}

function addWindows(parent: THREE.Object3D, rng: () => number, radius: number, height: number, color: number) {
  const geo = new THREE.PlaneGeometry(0.2, 0.3);
  const mat = windowMat(color);
  const rows = Math.max(1, Math.floor(height / 0.75));
  for (let r = 0; r < rows; r++) {
    const count = 7 + Math.floor(rng() * 4);
    const y = 0.5 + r * 0.72;
    for (let i = 0; i < count; i++) {
      const a = (i / count) * Math.PI * 2 + rng() * 0.1;
      const w = new THREE.Mesh(geo, mat);
      w.position.set(Math.cos(a) * (radius + 0.01), y, Math.sin(a) * (radius + 0.01));
      w.lookAt(w.position.x * 3, y, w.position.z * 3);
      parent.add(w);
    }
  }
}

function makeFlag(rng: () => number) {
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 1.3, 6), goldMat());
  pole.position.y = 0.65;
  const cloth = new THREE.Mesh(
    new THREE.PlaneGeometry(0.55, 0.32, 6, 1),
    new THREE.MeshStandardMaterial({
      color: PAINT[(rng() * PAINT.length) | 0],
      side: THREE.DoubleSide,
      roughness: 0.6,
      emissiveIntensity: 0.2,
    }),
  );
  cloth.position.set(0.28, 1.1, 0);
  const group = new THREE.Group();
  group.add(pole, cloth);
  group.userData.cloth = cloth;
  return group;
}

/** One palace/haveli tower: banded body, jharokha windows, dome and corner chhatris. */
function makeTower(rng: () => number, height: number, radius: number, grand: boolean) {
  const g = new THREE.Group();

  const plinth = new THREE.Mesh(
    new THREE.CylinderGeometry(radius * 1.22, radius * 1.34, 0.35, 12),
    wallMat(0xf0dcb8),
  );
  plinth.position.y = 0.17;
  plinth.castShadow = true;
  plinth.receiveShadow = true;
  g.add(plinth);

  const body = new THREE.Mesh(
    new THREE.CylinderGeometry(radius, radius * 1.06, height, 12),
    wallMat(WALLS[(rng() * WALLS.length) | 0]),
  );
  body.position.y = height / 2 + 0.3;
  body.castShadow = true;
  body.receiveShadow = true;
  g.add(body);

  // painted band — the thing that makes these read as Rajasthani rather than generic
  const bandColor = PAINT[(rng() * PAINT.length) | 0];
  const band = new THREE.Mesh(
    new THREE.CylinderGeometry(radius * 1.03, radius * 1.03, height * 0.26, 12),
    paintMat(bandColor),
  );
  band.position.y = 0.3 + height * (0.3 + rng() * 0.35);
  band.castShadow = true;
  g.add(band);

  // Grand towers get a wide roof terrace for the corner pavilions to stand on.
  const corniceR = grand ? radius * 1.62 : radius * 1.2;
  const cornice = new THREE.Mesh(
    new THREE.CylinderGeometry(corniceR, radius * 1.05, 0.2, 12),
    wallMat(0xfff4e2),
  );
  cornice.position.y = height + 0.3;
  cornice.castShadow = true;
  cornice.receiveShadow = true;
  g.add(cornice);

  addWindows(g, rng, radius * 1.01, height, rng() > 0.5 ? 0x4fd8ff : 0xffd166);

  const roofColor = ROOFS[(rng() * ROOFS.length) | 0];
  addDome(g, radius * 0.95, height + 0.38, roofColor);

  if (grand) {
    const ring = corniceR * 0.78;
    for (let i = 0; i < 4; i++) {
      const a = (i / 4) * Math.PI * 2 + Math.PI / 4;
      const c = addChhatri(g, 0.75, height + 0.4, radius * 0.3, ROOFS[(i + 1) % ROOFS.length]);
      c.position.x = Math.cos(a) * ring;
      c.position.z = Math.sin(a) * ring;
    }
    const flag = makeFlag(rng);
    flag.position.y = height + radius * 1.6;
    g.add(flag);
    g.userData.flag = flag;
  }

  return g;
}

export function buildCity() {
  const rng = mulberry32(20261121);
  const group = new THREE.Group();
  const buildings: THREE.Object3D[] = [];
  const flags: THREE.Group[] = [];

  // Island + ghat steps down to the water.
  const island = new THREE.Mesh(new THREE.CylinderGeometry(19, 20.5, 1.6, 64), wallMat(0xe8c99a));
  island.position.y = -0.8;
  island.receiveShadow = true;
  group.add(island);

  for (let i = 0; i < 4; i++) {
    const step = new THREE.Mesh(
      new THREE.CylinderGeometry(19 + i * 0.9, 19.6 + i * 0.9, 0.22, 64),
      wallMat(i % 2 ? 0xf0dcb8 : 0xe0b98a),
    );
    step.position.y = -0.2 - i * 0.24;
    step.receiveShadow = true;
    group.add(step);
  }

  const plaza = new THREE.Mesh(new THREE.CylinderGeometry(17.4, 17.4, 0.12, 64), paintMat(0xf6e3c4));
  plaza.position.y = 0.06;
  plaza.receiveShadow = true;
  group.add(plaza);

  // Centrepiece palace.
  const palace = makeTower(rng, 7.4, 2.5, true);
  palace.userData.baseY = 0;
  palace.userData.phase = 0;
  group.add(palace);
  buildings.push(palace);
  if (palace.userData.flag) flags.push(palace.userData.flag as THREE.Group);

  // Inner ring of havelis, outer ring of low town.
  const rings = [
    { count: 9, radius: 7.6, minH: 3.4, maxH: 5.6, minR: 0.95, maxR: 1.45, grandChance: 0.55 },
    { count: 14, radius: 12.4, minH: 2.2, maxH: 4.0, minR: 0.8, maxR: 1.2, grandChance: 0.25 },
    { count: 18, radius: 15.9, minH: 1.3, maxH: 2.6, minR: 0.62, maxR: 0.95, grandChance: 0.08 },
  ];

  for (const ring of rings) {
    for (let i = 0; i < ring.count; i++) {
      const a = (i / ring.count) * Math.PI * 2 + rng() * 0.16;
      const r = ring.radius + (rng() - 0.5) * 1.6;
      const h = ring.minH + rng() * (ring.maxH - ring.minH);
      const rad = ring.minR + rng() * (ring.maxR - ring.minR);
      const t = makeTower(rng, h, rad, rng() < ring.grandChance);
      t.position.set(Math.cos(a) * r, 0, Math.sin(a) * r);
      t.rotation.y = rng() * Math.PI;
      t.userData.baseY = 0;
      t.userData.phase = rng() * Math.PI * 2;
      group.add(t);
      buildings.push(t);
      if (t.userData.flag) flags.push(t.userData.flag as THREE.Group);
    }
  }

  // Free-standing chhatris along the waterfront.
  for (let i = 0; i < 10; i++) {
    const a = (i / 10) * Math.PI * 2 + 0.3;
    const c = addChhatri(group, 1.9, 0.2, 0.62, ROOFS[i % ROOFS.length]);
    c.position.set(Math.cos(a) * 18, 0.2, Math.sin(a) * 18);
    c.userData.baseY = 0.2;
    c.userData.phase = rng() * Math.PI * 2;
    buildings.push(c);
  }

  const backOut = (x: number) => 1 + 2.4 * (x - 1) ** 3 + 1.4 * (x - 1) ** 2;

  function update(t: number) {
    for (const [i, b] of buildings.entries()) {
      const phase = b.userData.phase as number;
      const base = b.userData.baseY as number;
      // Staggered rise out of the island, then a slow float.
      const r = Math.min(Math.max((t - i * 0.022) / 1.3, 0), 1);
      const e = backOut(r);
      b.scale.y = 0.15 + 0.85 * e;
      b.position.y = base - (1 - e) * 9 + Math.sin(t * 0.55 + phase) * 0.055 * r;
    }
    for (const flag of flags) {
      const cloth = flag.userData.cloth as THREE.Mesh;
      cloth.rotation.y = Math.sin(t * 2.4) * 0.5;
      cloth.scale.x = 0.85 + Math.sin(t * 3.1) * 0.15;
    }
  }

  return { group, buildings, update };
}

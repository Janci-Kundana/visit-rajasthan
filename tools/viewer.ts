/**
 * Dev-only QA harness for the Blender isometric tiles.
 *
 * Renders every exported tile in a grid under the same isometric camera and
 * lighting the site uses, so a browser screenshot is a faithful check of what
 * Blender actually produced. Not part of the shipped site.
 *
 * Query params:
 *   ?models=a,b,c   slugs to load (default: all four destinations)
 *   ?cell=460       pixel size of each cell
 *   ?bg=eaf2fa      cell background
 */
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { MeshoptDecoder } from "three/examples/jsm/libs/meshopt_decoder.module.js";
import { lightTile } from "../src/three/tileLighting";

const params = new URLSearchParams(location.search);
const slugs = (params.get("models") ?? "jaisalmer,jaipur,udaipur,jawai").split(",").filter(Boolean);
const CELL = Number(params.get("cell") ?? 460);
const BG = "#" + (params.get("bg") ?? "eaf2fa");
const dir = params.get("dir") ?? "/models";
const suffix = params.get("suffix") ?? "_tile";

const grid = document.getElementById("grid")!;
const loader = new GLTFLoader();
loader.setMeshoptDecoder(MeshoptDecoder);

type Report = { slug: string; ok: boolean; note: string };
const reports: Report[] = [];

function makeCell(slug: string) {
  const cell = document.createElement("div");
  cell.className = "cell";
  cell.style.width = `${CELL}px`;
  cell.style.height = `${CELL}px`;
  const tag = document.createElement("div");
  tag.className = "tag";
  tag.textContent = slug;
  cell.appendChild(tag);
  grid.appendChild(cell);
  return cell;
}

function renderInto(cell: HTMLElement, root: THREE.Object3D) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setSize(CELL, CELL, false);
  cell.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(BG);

  // Frame the tile: fit an orthographic camera to the model's bounding sphere.
  const box = new THREE.Box3().setFromObject(root);
  const sphere = box.getBoundingSphere(new THREE.Sphere());
  const centre = sphere.center;

  const d = sphere.radius * 1.28;
  const cam = new THREE.OrthographicCamera(-d, d, d, -d, 0.01, sphere.radius * 40);
  // True isometric-ish three-quarter view, matching the reference framing.
  const az = Math.PI * 0.25;
  const el = Math.atan(1 / Math.SQRT2) * 1.06;
  const r = sphere.radius * 8;
  cam.position.set(
    centre.x + r * Math.cos(el) * Math.cos(az),
    centre.y + r * Math.sin(el),
    centre.z + r * Math.cos(el) * Math.sin(az),
  );
  cam.lookAt(centre);

  // Recenter before applying the same outdoor lighting as the production cards.
  root.position.sub(centre);
  cam.position.sub(centre);
  cam.lookAt(0, 0, 0);
  lightTile(renderer, scene, sphere.radius);

  scene.add(root);
  renderer.render(scene, cam);
  return { box, sphere };
}

async function load(slug: string) {
  const cell = makeCell(slug);
  const url = `${dir}/${slug}${suffix}.glb`;
  try {
    const gltf = await loader.loadAsync(url);
    const root = gltf.scene;
    let meshes = 0;
    let tris = 0;
    root.traverse((o) => {
      const m = o as THREE.Mesh;
      if (!m.isMesh) return;
      meshes++;
      m.castShadow = true;
      m.receiveShadow = true;
      const materials = Array.isArray(m.material) ? m.material : [m.material];
      if (materials.every((material) => material.name.endsWith("_water"))) m.castShadow = false;
      const g = m.geometry as THREE.BufferGeometry;
      tris += (g.index ? g.index.count : g.attributes.position.count) / 3;
    });
    const { box } = renderInto(cell, root);
    const size = box.getSize(new THREE.Vector3());
    const note = `${meshes} meshes · ${Math.round(tris).toLocaleString()} tris · ${size.x.toFixed(1)}×${size.y.toFixed(1)}×${size.z.toFixed(1)}`;
    reports.push({ slug, ok: true, note });
    cell.querySelector(".tag")!.textContent = `${slug} — ${note}`;
  } catch (err) {
    const e = document.createElement("div");
    e.className = "err";
    e.textContent = `FAILED: ${(err as Error).message}`;
    cell.appendChild(e);
    reports.push({ slug, ok: false, note: String((err as Error).message) });
  }
}

for (const slug of slugs) await load(slug);

(window as unknown as { __qa: Report[] }).__qa = reports;
(window as unknown as { __ready: boolean }).__ready = true;
console.log("[QA] ready", JSON.stringify(reports));

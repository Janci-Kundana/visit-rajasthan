"""
Builds public/models/jaisalmer_iso.glb — the low-poly isometric city diorama,
in the visual genre of the isometric weather-app reference (thick base slab,
toy-diorama skyline, soft even lighting).
Run: /Applications/Blender.app/Contents/MacOS/Blender --background --python jaisalmer_iso.py
"""
import bpy, sys, os, math, random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import rajasthan_kit as kit

PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
OUT_GLB = os.path.join(PROJECT_ROOT, "public", "models", "jaisalmer_iso.glb")
PREVIEW_DIR = os.path.join(PROJECT_ROOT, "public", "models", "previews")

random.seed(7)

kit.clear_scene()

SLAB_SIZE = 13.0
SLAB_THICK = 1.6

sandstone = kit.procedural_sandstone_material("SandstoneIso", base_hex=(0.82, 0.63, 0.35), dark_hex=(0.44, 0.29, 0.16))
slab_mat = kit.flat_material("SlabStone", (0.86, 0.83, 0.76), roughness=0.7)
road_mat = kit.flat_material("Road", (0.42, 0.40, 0.38), roughness=0.85)
green_mat = kit.flat_material("Foliage", (0.16, 0.55, 0.20), roughness=0.8)
water_mat = kit.flat_material("Water", (0.05, 0.55, 0.58), roughness=0.12, metallic=0.15)
trim_mats = [
    kit.flat_material("TrimBlue", (0.08, 0.22, 0.45), roughness=0.5),
    kit.flat_material("TrimOchre", (0.75, 0.45, 0.08), roughness=0.5),
    kit.flat_material("TrimRed", (0.55, 0.10, 0.09), roughness=0.5),
]

parts = []

# ---------------------------------------------------------------- base slab
slab = kit.cube("Slab", (SLAB_SIZE, SLAB_SIZE, SLAB_THICK), (0, 0, -SLAB_THICK / 2), material=slab_mat)
kit.bevel(slab, width=0.12, segments=3)
parts.append(slab)

# a short road strip across the slab
road = kit.cube("Road", (SLAB_SIZE * 0.92, 1.6, 0.03), (0, -2.6, 0.02), material=road_mat)
parts.append(road)
for x in [-4.2, -1.4, 1.4, 4.2]:
    dash = kit.cube(f"Dash_{x}", (0.6, 0.12, 0.04), (x, -2.6, 0.04), material=slab_mat)
    parts.append(dash)

# ---------------------------------------------------------------- centerpiece: fort/palace
def sandstone_block(name, size, loc, rot_z=0):
    b = kit.cube(name, size, loc, material=sandstone)
    b.rotation_euler[2] = math.radians(rot_z)
    return b

fort_group = []
fort_group.append(sandstone_block("PalaceBase", (3.4, 3.0, 1.6), (0.8, 1.6, 0.8)))
fort_group.append(sandstone_block("PalaceMid", (2.6, 2.2, 1.4), (0.8, 1.6, 1.9)))
fort_group.append(sandstone_block("PalaceTop", (1.7, 1.5, 1.2), (0.8, 1.6, 3.0)))
for ti, (cx, cy) in enumerate([(-0.15, 0.75), (1.75, 0.75), (-0.15, 2.45), (1.75, 2.45)]):
    fort_group.append(kit.cylinder("PalaceTurret", 0.32, 1.6, (cx, cy, 3.7), segments=8, material=sandstone))
    fort_group.append(kit.dome("PalaceTurretCap", 0.36, (cx, cy, 4.5), material=sandstone, segments=10, ring_count=5))
    band = kit.cylinder(f"TurretBand_{ti}", 0.36, 0.6, (cx, cy, 3.55), segments=8, material=trim_mats[ti % len(trim_mats)])
    parts.append(band)

palace_door = kit.cube("PalaceDoor", (1.1, 0.14, 1.0), (0.8, 0.15, 0.5), material=trim_mats[0])
parts.append(palace_door)
pillar = kit.cylinder("PalaceChhatriPillar", 0.22, 0.9, (0.8, 1.6, 3.95), segments=8, material=sandstone)
fort_group.append(pillar)
domecap = kit.dome("PalaceChhatriDome", 0.55, (0.8, 1.6, 4.45), material=sandstone, segments=10, ring_count=5)
fort_group.append(domecap)
parts.extend(fort_group)

# ---------------------------------------------------------------- havelis
haveli_specs = [
    (-3.6, 2.3, 1.0, 1.3, 1.8, -10),
    (-2.0, -3.4, 1.15, 1.5, 2.3, 15),
    (3.4, -1.6, 0.95, 1.2, 1.6, 20),
    (-4.4, -1.2, 0.85, 1.1, 1.4, -5),
]
for i, (x, y, hw, hd, hh, rot) in enumerate(haveli_specs):
    body = sandstone_block(f"Haveli_{i}", (hw, hd, hh), (x, y, hh / 2), rot_z=rot)
    parts.append(body)
    # jharokha balcony detail: a thin protruding ledge partway up
    ledge = sandstone_block(f"HaveliLedge_{i}", (hw * 0.9, hd * 1.18, 0.08), (x, y, hh * 0.62), rot_z=rot)
    parts.append(ledge)
    trim = kit.cube(f"Trim_{i}", (hw * 0.9, hd * 1.15, hh * 0.48), (x, y, hh * 0.26), material=trim_mats[i % len(trim_mats)])
    trim.rotation_euler[2] = math.radians(rot)
    parts.append(trim)

# small chhatri accent near the havelis
ch_pillar = kit.cylinder("SmallChhatriPillar", 0.16, 0.7, (3.6, 3.4, 0.35), segments=8, material=sandstone)
parts.append(ch_pillar)
ch_dome = kit.dome("SmallChhatriDome", 0.42, (3.6, 3.4, 0.72), material=sandstone, segments=10, ring_count=5)
parts.append(ch_dome)

# ---------------------------------------------------------------- trees (low-poly)
def tree(x, y, scale=1.0):
    trunk = kit.cylinder(f"TreeTrunk_{x}_{y}", 0.08 * scale, 0.5 * scale, (x, y, 0.25 * scale), segments=6, material=road_mat)
    parts.append(trunk)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.42 * scale, location=(x, y, 0.75 * scale))
    top = bpy.context.active_object
    top.name = f"TreeTop_{x}_{y}"
    top.data.materials.append(green_mat)
    parts.append(top)

for (tx, ty, ts) in [(5.2, 1.2, 1.0), (5.5, -3.0, 0.85), (-5.4, 3.6, 0.9), (-1.0, 4.4, 0.75), (2.6, 4.0, 0.8)]:
    tree(tx, ty, ts)

# a small reservoir corner (nod to Gadisar Lake)
bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=1.5, depth=0.06, location=(-4.6, -4.2, 0.03))
lake = bpy.context.active_object
lake.name = "Lake"
lake.data.materials.append(water_mat)
parts.append(lake)

# ---------------------------------------------------------------- join non-slab architecture, bevel, bake
architecture = [p for p in parts if p.name.startswith(("Palace", "Haveli", "SmallChhatri"))]
other = [p for p in parts if p not in architecture]

fort_arch = kit.join(architecture, "IsoArchitecture")
kit.bevel(fort_arch, width=0.02, segments=1)
kit.bake_procedural_to_texture(fort_arch, sandstone, size=1024, samples=20)

all_objs = [fort_arch] + other
kit.export_glb(OUT_GLB, objects=all_objs)

tri_count = sum(len(o.data.polygons) for o in all_objs if o.data)
print(f"ISO TOTAL POLY COUNT: {tri_count}")
print(f"Exported: {OUT_GLB}")

# ---------------------------------------------------------------- preview render (matches iso camera: elev ~37, azim 45)
import mathutils
cam_dist = 22
elev = math.radians(37)
azim = math.radians(45)
cam_loc = (
    cam_dist * math.cos(elev) * math.cos(azim),
    cam_dist * math.cos(elev) * math.sin(azim),
    cam_dist * math.sin(elev),
)
kit.setup_preview_camera_and_light(cam_loc, target=(0, 0, -0.2), light_energy=4.0)
for o in bpy.context.scene.objects:
    if o.type == "CAMERA":
        o.data.lens = 40
kit.render_preview(os.path.join(PREVIEW_DIR, "jaisalmer_iso_hero.png"), resolution=900, samples=48)

print("DONE jaisalmer_iso.py")

"""
Builds public/models/udaipur_iso.glb — the low-poly isometric city diorama for
Udaipur: pale marble palace + a corner of Lake Pichola with a tiny island nod
to Jag Mandir, plus haveli buildings each carrying a distinct saturated accent
color rather than a uniform monochrome palette.
Run: /Applications/Blender.app/Contents/MacOS/Blender --background --python udaipur_iso.py
"""
import bpy, sys, os, math, random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import rajasthan_kit as kit

PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
OUT_GLB = os.path.join(PROJECT_ROOT, "public", "models", "udaipur_iso.glb")
PREVIEW_DIR = os.path.join(PROJECT_ROOT, "public", "models", "previews")

random.seed(29)

kit.clear_scene()

SLAB_SIZE = 13.0
SLAB_THICK = 1.6

marble = kit.procedural_sandstone_material("MarbleIso", base_hex=(0.90, 0.88, 0.81), dark_hex=(0.70, 0.66, 0.56))
slab_mat = kit.flat_material("SlabStoneIso", (0.87, 0.85, 0.80), roughness=0.65)
water_mat = kit.flat_material("WaterIso", (0.02, 0.55, 0.58), roughness=0.12, metallic=0.08)
dome_cream = kit.flat_material("DomeCreamIso", (0.93, 0.86, 0.64), roughness=0.35)
gold_trim = kit.flat_material("GoldTrimIso", (0.85, 0.62, 0.15), roughness=0.3, metallic=0.2)
green_mat = kit.flat_material("FoliageVivid", (0.10, 0.62, 0.20), roughness=0.7)
pot_mat = kit.flat_material("PotTerracotta", (0.55, 0.28, 0.15), roughness=0.7)
plant_red = kit.flat_material("PottedPlantRed", (0.85, 0.22, 0.08), roughness=0.6)
plant_orange = kit.flat_material("PottedPlantOrange", (0.90, 0.48, 0.06), roughness=0.6)
haveli_blue = kit.flat_material("HaveliBlue", (0.06, 0.30, 0.55), roughness=0.5)
haveli_ochre = kit.flat_material("HaveliOchre", (0.80, 0.55, 0.10), roughness=0.5)
haveli_terracotta = kit.flat_material("HaveliTerracotta", (0.75, 0.30, 0.15), roughness=0.55)

parts = []

# ---------------------------------------------------------------- base slab
slab = kit.cube("Slab", (SLAB_SIZE, SLAB_SIZE, SLAB_THICK), (0, 0, -SLAB_THICK / 2), material=slab_mat)
kit.bevel(slab, width=0.12, segments=3)
parts.append(slab)

# ---------------------------------------------------------------- Lake Pichola corner + tiny island
lake = kit.cube("Lake", (5.6, 5.0, 0.05), (-3.7, -3.1, 0.025), material=water_mat)
parts.append(lake)
kit.bevel(lake, width=0.15, segments=2)

island_base = kit.cube("IslandBase", (0.55, 0.55, 0.22), (-3.9, -3.4, 0.11), material=marble)
parts.append(island_base)
island_dome = kit.dome("IslandDome", 0.28, (-3.9, -3.4, 0.22), material=dome_cream, segments=10, ring_count=5)
parts.append(island_dome)

# ---------------------------------------------------------------- centerpiece: City Palace (simplified)
PX, PY = 1.0, 1.6

def marble_block(name, size, loc, rot_z=0):
    b = kit.cube(name, size, loc, material=marble)
    b.rotation_euler[2] = math.radians(rot_z)
    return b

parts.append(marble_block("PalaceBase", (3.4, 3.0, 1.6), (PX, PY, 0.8)))
parts.append(marble_block("PalaceMid", (2.6, 2.2, 1.4), (PX, PY, 1.9)))
parts.append(marble_block("PalaceTop", (1.7, 1.5, 1.2), (PX, PY, 3.0)))

for cx, cy in [(PX - 0.95, PY - 0.85), (PX + 0.95, PY - 0.85), (PX - 0.95, PY + 0.85), (PX + 0.95, PY + 0.85)]:
    parts.append(kit.cylinder("PalaceTurret", 0.32, 1.6, (cx, cy, 3.7), segments=8, material=dome_cream))
    parts.append(kit.dome("PalaceTurretCap", 0.36, (cx, cy, 4.5), material=dome_cream, segments=10, ring_count=5))

# gold-trimmed central chhatri — the tallest point, matching the hero model's accent
parts.append(kit.cylinder("PalaceChhatriTrim", 0.62, 0.1, (PX, PY, 3.9), segments=12, material=gold_trim))
parts.append(kit.cylinder("PalaceChhatriPillar", 0.22, 0.9, (PX, PY, 3.95), segments=8, material=gold_trim))
parts.append(kit.dome("PalaceChhatriDome", 0.55, (PX, PY, 4.45), material=dome_cream, segments=10, ring_count=5))

# a small teal-blue painted door on the palace's lake-facing front
parts.append(kit.cube("PalaceDoor", (0.55, 0.08, 0.75), (PX, PY - 1.58, 0.5), material=haveli_blue))

# ---------------------------------------------------------------- havelis — each a distinct accent color
haveli_specs = [
    # x,    y,    hw,  hd,  hh,  rot,  accent_material
    (-3.6, 3.0, 1.0, 1.3, 1.8, -10, haveli_blue),
    (4.0, -1.2, 1.15, 1.5, 2.3, 15, haveli_ochre),
    (4.4, 3.2, 0.95, 1.2, 1.6, 20, haveli_terracotta),
]
for i, (x, y, hw, hd, hh, rot, accent) in enumerate(haveli_specs):
    body = marble_block(f"Haveli_{i}", (hw, hd, hh), (x, y, hh / 2), rot_z=rot)
    parts.append(body)
    # jharokha ledge
    ledge = marble_block(f"HaveliLedge_{i}", (hw * 0.9, hd * 1.18, 0.08), (x, y, hh * 0.62), rot_z=rot)
    parts.append(ledge)
    # saturated accent band across the lower facade
    band = kit.cube(f"HaveliAccent_{i}", (hw * 0.92, hd * 1.02, hh * 0.32), (x, y, hh * 0.16), material=accent)
    band.rotation_euler[2] = math.radians(rot)
    parts.append(band)

# ---------------------------------------------------------------- trees (vivid green)
def tree(x, y, scale=1.0):
    trunk = kit.cylinder(f"TreeTrunk_{x}_{y}", 0.08 * scale, 0.5 * scale, (x, y, 0.25 * scale), segments=6, material=pot_mat)
    parts.append(trunk)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.42 * scale, location=(x, y, 0.75 * scale))
    top = bpy.context.active_object
    top.name = f"TreeTop_{x}_{y}"
    top.data.materials.append(green_mat)
    parts.append(top)

for (tx, ty, ts) in [(5.6, 1.2, 1.0), (5.0, -3.6, 0.85), (-5.2, 4.2, 0.9), (-0.8, 4.6, 0.75), (2.6, 4.4, 0.8)]:
    tree(tx, ty, ts)

# ---------------------------------------------------------------- potted plant accents near the palace
def potted_plant(x, y, plant_material):
    pot = kit.cylinder(f"Pot_{x}_{y}", 0.16, 0.24, (x, y, 0.12), segments=8, material=pot_mat)
    parts.append(pot)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.19, location=(x, y, 0.34))
    top = bpy.context.active_object
    top.name = f"PottedTop_{x}_{y}"
    top.data.materials.append(plant_material)
    parts.append(top)

potted_plant(PX - 1.9, PY - 1.7, plant_red)
potted_plant(PX + 1.9, PY - 1.7, plant_orange)

# ---------------------------------------------------------------- join marble architecture only, bevel, bake
architecture = [p for p in parts if p.name.startswith(("Palace", "Haveli")) and "Turret" not in p.name and "Chhatri" not in p.name and "Accent" not in p.name and "Door" not in p.name]
other = [p for p in parts if p not in architecture]

palace_arch = kit.join(architecture, "IsoArchitecture")
kit.bevel(palace_arch, width=0.02, segments=1)
kit.bake_procedural_to_texture(palace_arch, marble, size=1024, samples=20)

all_objs = [palace_arch] + other
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
kit.render_preview(os.path.join(PREVIEW_DIR, "udaipur_iso_hero.png"), resolution=900, samples=48)

print("DONE udaipur_iso.py")

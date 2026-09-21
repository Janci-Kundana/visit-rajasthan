"""
Builds public/models/jaipur_iso.glb — the low-poly isometric city diorama for Jaipur,
"The Pink City", with saturated color accents (per-haveli trim colors, vivid green
trees, a contrasting-stone Jantar Mantar gnomon) so it doesn't read as flat pink.
Run: /Applications/Blender.app/Contents/MacOS/Blender --background --python jaipur_iso.py
"""
import bpy, sys, os, math, random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import rajasthan_kit as kit

PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
OUT_GLB = os.path.join(PROJECT_ROOT, "public", "models", "jaipur_iso.glb")
PREVIEW_DIR = os.path.join(PROJECT_ROOT, "public", "models", "previews")

random.seed(19)
kit.clear_scene()

SLAB_SIZE = 13.0
SLAB_THICK = 1.6

sandstone = kit.procedural_sandstone_material("SandstonePinkIso", base_hex=(0.80, 0.46, 0.34), dark_hex=(0.40, 0.19, 0.13))
slab_mat = kit.flat_material("SlabStone", (0.86, 0.83, 0.76), roughness=0.7)
road_mat = kit.flat_material("Road", (0.42, 0.40, 0.38), roughness=0.85)
green_mat = kit.flat_material("Foliage", (0.12, 0.62, 0.22), roughness=0.75)
gnomon_mat = kit.flat_material("GnomonStone", (0.78, 0.77, 0.72), roughness=0.55)

TRIM_COLORS = [
    ("Blue", (0.10, 0.30, 0.55)),
    ("Mustard", (0.75, 0.55, 0.08)),
    ("Teal", (0.05, 0.45, 0.42)),
]
trim_mats = {name: kit.flat_material(f"Trim{name}", col, roughness=0.5) for name, col in TRIM_COLORS}


def polar(radius, angle_deg, z, cx=0.0, cy=0.0):
    a = math.radians(angle_deg)
    return (cx + radius * math.cos(a), cy + radius * math.sin(a), z)


parts = []
trim_parts = []

# ---------------------------------------------------------------- base slab
slab = kit.cube("Slab", (SLAB_SIZE, SLAB_SIZE, SLAB_THICK), (0, 0, -SLAB_THICK / 2), material=slab_mat)
kit.bevel(slab, width=0.12, segments=3)
parts.append(slab)

road = kit.cube("Road", (SLAB_SIZE * 0.92, 1.6, 0.03), (0, -2.6, 0.02), material=road_mat)
parts.append(road)
for x in [-4.2, -1.4, 1.4, 4.2]:
    dash = kit.cube(f"Dash_{x}", (0.6, 0.12, 0.04), (x, -2.6, 0.04), material=slab_mat)
    parts.append(dash)

# ---------------------------------------------------------------- centerpiece: simplified curved Hawa Mahal
MAHAL_CX, MAHAL_CY = 0.8, 1.6
mahal_group = []
tiers = [(2.6, 1.6, 0.9), (2.0, 1.35, 1.9), (1.4, 1.05, 2.8)]
arc = 70.0
for ti, (radius, seg_h, z0) in enumerate(tiers):
    deg = -arc
    i = 0
    while deg <= arc:
        loc = polar(radius, deg, z0 + seg_h / 2, MAHAL_CX, MAHAL_CY)
        seg = kit.cube(f"MahalSeg_{ti}_{deg:.0f}", (0.42, 0.34, seg_h * 0.85), loc, material=sandstone)
        seg.rotation_euler[2] = math.radians(deg + 90)
        mahal_group.append(seg)
        if i % 2 == 0:
            t_name = TRIM_COLORS[(ti + i) % len(TRIM_COLORS)][0]
            trim_loc = polar(radius + 0.2, deg, z0 + seg_h * 0.55, MAHAL_CX, MAHAL_CY)
            trim = kit.cube(f"MahalTrim_{ti}_{deg:.0f}", (0.22, 0.06, seg_h * 0.55), trim_loc, material=trim_mats[t_name])
            trim.rotation_euler[2] = math.radians(deg + 90)
            trim_parts.append(trim)
        i += 1
        deg += 14
    arc *= 0.8

crown_r = tiers[-1][0]
crown_z = tiers[-1][2] + tiers[-1][1]
for deg in (-20, 0, 20):
    pillar = kit.cylinder(f"MahalCrownPillar_{deg}", 0.14, 0.5, polar(crown_r, deg, crown_z + 0.25, MAHAL_CX, MAHAL_CY), segments=8, material=sandstone)
    mahal_group.append(pillar)
    dome = kit.dome(f"MahalCrownDome_{deg}", 0.34, polar(crown_r, deg, crown_z + 0.5, MAHAL_CX, MAHAL_CY), material=sandstone, segments=10, ring_count=5)
    mahal_group.append(dome)

parts.extend(mahal_group)

# ---------------------------------------------------------------- havelis, each with a distinct saturated accent
haveli_specs = [
    (-3.6, 2.3, 1.0, 1.3, 1.8, -10, "Blue"),
    (-2.0, -3.4, 1.15, 1.5, 2.3, 15, "Mustard"),
    (3.4, -1.6, 0.95, 1.2, 1.6, 20, "Teal"),
]
for i, (x, y, hw, hd, hh, rot, tname) in enumerate(haveli_specs):
    body = kit.cube(f"Haveli_{i}", (hw, hd, hh), (x, y, hh / 2), material=sandstone)
    body.rotation_euler[2] = math.radians(rot)
    parts.append(body)
    ledge = kit.cube(f"HaveliLedge_{i}", (hw * 0.9, hd * 1.18, 0.08), (x, y, hh * 0.62), material=sandstone)
    ledge.rotation_euler[2] = math.radians(rot)
    parts.append(ledge)
    trim = kit.cube(f"HaveliTrim_{i}", (hw * 0.96, hd * 1.08, hh * 0.5), (x, y, hh * 0.27), material=trim_mats[tname])
    trim.rotation_euler[2] = math.radians(rot)
    trim_parts.append(trim)

# ---------------------------------------------------------------- Jantar Mantar gnomon (contrasting pale stone)
gnomon = kit.cube("JantarGnomon", (0.18, 1.6, 0.05), (4.6, 3.0, 1.0), material=gnomon_mat)
gnomon.rotation_euler[0] = math.radians(35)
parts.append(gnomon)
gnomon_base = kit.cube("JantarBase", (0.9, 0.9, 0.3), (4.6, 3.0, 0.15), material=gnomon_mat)
parts.append(gnomon_base)

# ---------------------------------------------------------------- trees (vivid green, not olive-drab)
def tree(x, y, scale=1.0):
    trunk = kit.cylinder(f"TreeTrunk_{x}_{y}", 0.08 * scale, 0.5 * scale, (x, y, 0.25 * scale), segments=6, material=road_mat)
    parts.append(trunk)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.42 * scale, location=(x, y, 0.75 * scale))
    top = bpy.context.active_object
    top.name = f"TreeTop_{x}_{y}"
    top.data.materials.append(green_mat)
    parts.append(top)


for (tx, ty, ts) in [(5.2, 1.2, 1.0), (5.5, -3.0, 0.85), (-5.4, 3.6, 0.9), (-1.0, 4.4, 0.75), (2.6, 4.4, 0.8)]:
    tree(tx, ty, ts)

# ---------------------------------------------------------------- join non-slab architecture, bevel, bake
architecture = [p for p in parts if p.name.startswith(("MahalSeg", "MahalCrown", "Haveli"))]
other = [p for p in parts if p not in architecture]

iso_arch = kit.join(architecture, "IsoArchitecture")
kit.bevel(iso_arch, width=0.02, segments=1)
kit.bake_procedural_to_texture(iso_arch, sandstone, size=1024, samples=20)

trims = kit.join(trim_parts, "TrimAccents")

all_objs = [iso_arch, trims] + other
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
kit.render_preview(os.path.join(PREVIEW_DIR, "jaipur_iso_hero.png"), resolution=900, samples=48)

print("DONE jaipur_iso.py")

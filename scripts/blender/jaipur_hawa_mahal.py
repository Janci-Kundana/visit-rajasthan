"""
Builds public/models/jaipur_hawa_mahal.glb — the photoreal hero asset.
Hawa Mahal: a tall, flat, tapering pink-terracotta honeycomb facade with
saturated color accents (painted shutters, bunting, bougainvillea) so it
doesn't read as monochrome sandstone.
Run: /Applications/Blender.app/Contents/MacOS/Blender --background --python jaipur_hawa_mahal.py
"""
import bpy, sys, os, math, random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import rajasthan_kit as kit

PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
OUT_GLB = os.path.join(PROJECT_ROOT, "public", "models", "jaipur_hawa_mahal.glb")
PREVIEW_DIR = os.path.join(PROJECT_ROOT, "public", "models", "previews")

random.seed(11)
kit.clear_scene()

# ---------------------------------------------------------------- materials
sandstone = kit.procedural_sandstone_material("SandstonePink", base_hex=(0.80, 0.46, 0.34), dark_hex=(0.40, 0.19, 0.13))
plaza = kit.flat_material("Plaza", (0.58, 0.42, 0.36), roughness=0.85)

ACCENT_COLORS = [
    ("Blue", (0.10, 0.30, 0.55)),
    ("Teal", (0.05, 0.45, 0.42)),
    ("DeepRed", (0.55, 0.08, 0.10)),
]
accent_mats = {name: kit.flat_material(f"Shutter{name}", col, roughness=0.5) for name, col in ACCENT_COLORS}

BUNTING_COLORS = [
    ("Yellow", (0.85, 0.65, 0.05)),
    ("Red", (0.65, 0.08, 0.08)),
    ("Green", (0.10, 0.50, 0.20)),
    ("Blue", (0.10, 0.30, 0.55)),
    ("Orange", (0.85, 0.40, 0.05)),
]
bunting_mats = {name: kit.flat_material(f"Bunting{name}", col, roughness=0.6) for name, col in BUNTING_COLORS}

bougain_mag = kit.flat_material("BougainMagenta", (0.75, 0.10, 0.45), roughness=0.7)
bougain_org = kit.flat_material("BougainOrange", (0.85, 0.40, 0.05), roughness=0.7)


def polar(radius, angle_deg, z):
    a = math.radians(angle_deg)
    return (radius * math.cos(a), radius * math.sin(a), z)


facade_parts = []
shutter_parts = []
bunting_parts = []
foliage_parts = []

TIERS = 5
TIER_H = 1.75
BASE_R = 8.4
R_STEP = 0.55
STEP_DEG = 7.5
arc_half = 62.0

# ---------------------------------------------------------------- plaza ground (wide along the facade's Y-span)
ground = kit.cube("Plaza", (12.0, 17.0, 0.3), (3.0, 0.0, -0.15), material=plaza)

# ---------------------------------------------------------------- tapering tiers
for t in range(TIERS):
    z0 = t * TIER_H
    radius = BASE_R - t * R_STEP
    deg = -arc_half
    i = 0
    while deg <= arc_half:
        # structural wall segment, follows the curve (proven pattern from the Jaisalmer wall ring)
        seg = kit.cube(f"Wall_{t}_{deg:.0f}", (0.95, 0.85, TIER_H * 0.96), polar(radius, deg, z0 + TIER_H / 2), material=sandstone)
        seg.rotation_euler[2] = math.radians(deg + 90)
        facade_parts.append(seg)

        # proud jharokha window-bay module
        module = kit.cube(f"Jharokha_{t}_{deg:.0f}", (0.6, 0.30, TIER_H * 0.5), polar(radius + 0.28, deg, z0 + TIER_H * 0.6), material=sandstone)
        module.rotation_euler[2] = math.radians(deg + 90)
        facade_parts.append(module)

        # painted shutter/frame accent, cycling through saturated colors across the facade
        acc_name = ACCENT_COLORS[i % len(ACCENT_COLORS)][0]
        shutter = kit.cube(f"Shutter_{t}_{deg:.0f}", (0.28, 0.06, TIER_H * 0.3), polar(radius + 0.46, deg, z0 + TIER_H * 0.6), material=accent_mats[acc_name])
        shutter.rotation_euler[2] = math.radians(deg + 90)
        shutter_parts.append(shutter)

        i += 1
        deg += STEP_DEG

    arc_half *= 0.86  # each tier a touch narrower -> tapering silhouette

# ---------------------------------------------------------------- crown chhatris + strung bunting
crown_r = BASE_R - (TIERS - 1) * R_STEP
crown_z = TIERS * TIER_H
crown_degs = [-25, -12, 0, 12, 25]
for deg in crown_degs:
    pillar = kit.cylinder(f"CrownPillar_{deg}", 0.22, 0.9, polar(crown_r, deg, crown_z + 0.45), segments=8, material=sandstone)
    facade_parts.append(pillar)
    capdome = kit.dome(f"CrownDome_{deg}", 0.62, polar(crown_r, deg, crown_z + 0.95), material=sandstone, segments=10, ring_count=5)
    facade_parts.append(capdome)

bi = 0
deg = crown_degs[0]
while deg <= crown_degs[-1]:
    b_name = BUNTING_COLORS[bi % len(BUNTING_COLORS)][0]
    flag = kit.cylinder(f"Bunting_{deg:.0f}", 0.24, 0.42, polar(crown_r + 0.2, deg, crown_z + 0.15), segments=4, material=bunting_mats[b_name], cone_ratio=0.0)
    flag.rotation_euler[0] = math.radians(90)
    flag.rotation_euler[2] = math.radians(deg)
    bunting_parts.append(flag)
    bi += 1
    deg += 4.5

# ---------------------------------------------------------------- bougainvillea climbing the base
for i in range(14):
    deg = random.uniform(-55, 55)
    r = BASE_R + random.uniform(-0.3, 0.6)
    z = random.uniform(0.2, 2.4)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=random.uniform(0.4, 0.7), location=polar(r, deg, z))
    blob = bpy.context.active_object
    blob.name = f"Bougain_{i}"
    blob.scale.z *= 0.7
    blob.data.materials.append(bougain_mag if i % 2 == 0 else bougain_org)
    foliage_parts.append(blob)

# ---------------------------------------------------------------- simplified haveli rooftops flanking
for i, (dx, dy, w, d, h) in enumerate([(-6.0, 2.4, 2.4, 1.8, 4.2), (-5.6, -2.6, 2.1, 1.6, 3.6)]):
    body = kit.cube(f"HaveliRoof_{i}", (w, d, h), (dx, dy, h / 2), material=sandstone)
    facade_parts.append(body)

# ---------------------------------------------------------------- join, bevel, bake, export
mahal = kit.join(facade_parts, "HawaMahalFacade")
kit.bevel(mahal, width=0.02, segments=1)
print(f"HawaMahalFacade polys (pre-bake): {len(mahal.data.polygons)}")

kit.bake_procedural_to_texture(mahal, sandstone, size=1536, samples=24)

shutters = kit.join(shutter_parts, "Shutters")
bunting = kit.join(bunting_parts, "Bunting")
bougain = kit.join(foliage_parts, "Bougainvillea")

all_objs = [mahal, ground, shutters, bunting, bougain]
kit.export_glb(OUT_GLB, objects=all_objs)

tri_count = sum(len(o.data.polygons) for o in all_objs if o.data)
print(f"TOTAL POLY COUNT: {tri_count}")
print(f"Exported: {OUT_GLB}")

# ---------------------------------------------------------------- preview renders
kit.setup_preview_camera_and_light((22, -3, 9), target=(3, 0, 4.2), light_energy=4.5)
kit.render_preview(os.path.join(PREVIEW_DIR, "jaipur_hawa_mahal_hero.png"), resolution=900, samples=48)

for o in bpy.context.scene.objects:
    if o.type == "CAMERA":
        o.location = (16, 16, 15)
        import mathutils
        direction = mathutils.Vector((3, 0, 4.2)) - o.location
        o.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
kit.render_preview(os.path.join(PREVIEW_DIR, "jaipur_hawa_mahal_iso_angle.png"), resolution=900, samples=48)

print("DONE jaipur_hawa_mahal.py")

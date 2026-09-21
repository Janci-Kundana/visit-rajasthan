"""
Builds public/models/udaipur_palace.glb — the photoreal hero asset: the City
Palace on the edge of Lake Pichola. Pale marble/ivory walls, warm cream domes,
a stepped lakefront plinth down to a small reflective water plane.
Run: /Applications/Blender.app/Contents/MacOS/Blender --background --python udaipur_palace.py
"""
import bpy, sys, os, math, random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import rajasthan_kit as kit

PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
OUT_GLB = os.path.join(PROJECT_ROOT, "public", "models", "udaipur_palace.glb")
PREVIEW_DIR = os.path.join(PROJECT_ROOT, "public", "models", "previews")

random.seed(11)

kit.clear_scene()

marble = kit.procedural_sandstone_material("Marble", base_hex=(0.91, 0.89, 0.82), dark_hex=(0.72, 0.68, 0.58))
dome_cream = kit.flat_material("DomeCream", (0.93, 0.86, 0.64), roughness=0.35)
gold_trim = kit.flat_material("GoldTrim", (0.85, 0.62, 0.15), roughness=0.3, metallic=0.2)
painted_wood = kit.flat_material("PaintedWood", (0.02, 0.28, 0.44), roughness=0.35)
plinth_mat = kit.flat_material("Plinth", (0.80, 0.77, 0.68), roughness=0.6)
lakebed_mat = kit.flat_material("Lakebed", (0.22, 0.20, 0.17), roughness=0.9)
water_mat = kit.flat_material("LakeWater", (0.02, 0.55, 0.58), roughness=0.12, metallic=0.08)
boug_magenta = kit.flat_material("BougainvilleaMagenta", (0.78, 0.06, 0.42), roughness=0.65)
boug_orange = kit.flat_material("BougainvilleaOrange", (0.92, 0.40, 0.04), roughness=0.65)
flag_mats = [
    kit.flat_material("FlagRed", (0.75, 0.10, 0.10), roughness=0.5),
    kit.flat_material("FlagYellow", (0.88, 0.72, 0.10), roughness=0.5),
    kit.flat_material("FlagGreen", (0.13, 0.55, 0.24), roughness=0.5),
    kit.flat_material("FlagBlue", (0.10, 0.35, 0.75), roughness=0.5),
    kit.flat_material("FlagOrange", (0.88, 0.46, 0.08), roughness=0.5),
]

marble_parts = []
dome_parts = []  # flat-material accessories (domes, trims, doors, foliage, flags) — never baked, safe to mix materials

# ---------------------------------------------------------------- lakefront plinth + water
LAND_TOP = 0.0
land = kit.cube("LandPlinth", (16.0, 8.0, 1.2), (0, 2.5, LAND_TOP - 0.6), material=plinth_mat)

lakebed = kit.cube("Lakebed", (16.0, 7.0, 0.9), (0, -5.0, -0.86), material=lakebed_mat)
water = kit.cube("LakeWater", (16.0, 7.0, 0.06), (0, -5.0, -0.38), material=water_mat)

# ---------------------------------------------------------------- stepped palace tiers
TX, TY = 0.0, 2.2

tier1 = kit.cube("Tier1", (6.4, 4.4, 2.2), (TX, TY, 1.1), material=marble)
marble_parts.append(tier1)
ledge1 = kit.cube("Ledge1", (6.6, 4.6, 0.15), (TX, TY, 2.2 + 0.075), material=marble)
marble_parts.append(ledge1)

tier2 = kit.cube("Tier2", (4.8, 3.4, 2.0), (TX, TY, 3.2), material=marble)
marble_parts.append(tier2)
ledge2 = kit.cube("Ledge2", (5.0, 3.6, 0.15), (TX, TY, 4.2 + 0.075), material=marble)
marble_parts.append(ledge2)

tier3 = kit.cube("Tier3", (3.4, 2.6, 1.8), (TX, TY, 5.0), material=marble)
marble_parts.append(tier3)
ledge3 = kit.cube("Ledge3", (3.6, 2.8, 0.15), (TX, TY, 5.9 + 0.075), material=marble)
marble_parts.append(ledge3)

tower = kit.cube("Tower", (1.7, 1.7, 3.0), (TX, TY, 7.4), material=marble)
marble_parts.append(tower)

# central tower dome (tallest point) with a gold trim collar at its base
dome_parts.append(kit.cylinder("TowerDomeTrim", 1.1, 0.12, (TX, TY, 8.84), segments=14, material=gold_trim))
dome_parts.append(kit.dome("TowerDome", 1.05, (TX, TY, 8.9), material=dome_cream, segments=14, ring_count=7))
dome_parts.append(kit.cylinder("TowerFinial", 0.08, 0.5, (TX, TY, 9.9), segments=8, material=gold_trim))

# ---------------------------------------------------------------- arcade arches on tier1 front (facing the lake)
front_y = TY - 2.2  # tier1 front face
for ax in (-2.0, 0.0, 2.0):
    blk = kit.cube(f"Arcade_{ax}", (1.0, 0.5, 1.6), (ax, front_y - 0.1, 0.8), material=marble)
    cutter_loc = (ax, front_y - 0.1, 0.5)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.55, depth=2.0, location=cutter_loc)
    cutter = bpy.context.active_object
    cutter.rotation_euler = (math.radians(90), 0, 0)
    mod = blk.modifiers.new("ArchCut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cutter
    bpy.context.view_layer.objects.active = blk
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    marble_parts.append(blk)

    # deep teal-blue painted wooden door filling the whole arch opening (full door scale, not a plaque)
    door = kit.cube(f"ArcadeDoor_{ax}", (0.92, 0.16, 1.35), (ax, front_y - 0.08, 0.68), material=painted_wood)
    dome_parts.append(door)

# large painted-wood shutter panels flush on tier2's front face — sized to read clearly at hero distance
for sx in (-1.2, 1.2):
    shutter = kit.cube(f"Tier2Shutter_{sx}", (1.1, 0.08, 1.3), (sx, TY - 1.7 - 0.04, 3.15), material=painted_wood)
    dome_parts.append(shutter)

# ---------------------------------------------------------------- corner chhatris at varying roofline heights
def corner_chhatri(x, y, base_z, dome_r, pillar_h=0.5, material=dome_cream):
    p = kit.cylinder(f"ChhatriPillar_{x}_{y}", dome_r * 0.4, pillar_h, (x, y, base_z + pillar_h / 2), segments=8, material=material)
    dome_parts.append(p)
    d = kit.dome(f"ChhatriDome_{x}_{y}", dome_r, (x, y, base_z + pillar_h), material=material, segments=10, ring_count=5)
    dome_parts.append(d)

for x, y in [(-2.6, 0.5), (2.6, 0.5), (-2.6, 3.9), (2.6, 3.9)]:
    corner_chhatri(x, y, 2.2, 0.5)
for x, y in [(-2.0, 0.9), (2.0, 0.9), (-2.0, 3.5), (2.0, 3.5)]:
    corner_chhatri(x, y, 4.2, 0.45)
# two of the topmost corner chhatris get a gold/ochre trim instead of plain cream
corner_chhatri(-1.3, 1.3, 5.9, 0.4, material=gold_trim)
corner_chhatri(1.3, 3.1, 5.9, 0.4, material=gold_trim)
for x, y in [(1.3, 1.3), (-1.3, 3.1)]:
    corner_chhatri(x, y, 5.9, 0.4)

# ---------------------------------------------------------------- bougainvillea climbing both tier1 side walls —
# big enough clumps, spread across most of the wall, so it reads at hero-camera distance, not just up close
random.seed(23)
for wall_x, sign in ((3.15, 1), (-3.15, -1)):
    for i in range(20):
        bx = wall_x + sign * random.uniform(-0.06, 0.16)
        by = random.uniform(0.3, 4.1)
        bz = random.uniform(0.2, 2.15)
        r = random.uniform(0.22, 0.42)
        mat = random.choice((boug_magenta, boug_orange))
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=r, location=(bx, by, bz))
        leaf = bpy.context.active_object
        leaf.name = f"Bougainvillea_{wall_x}_{i}"
        leaf.data.materials.append(mat)
        dome_parts.append(leaf)

# ---------------------------------------------------------------- prayer-flag bunting strung across tier1's front,
# clear of the tier2 overhang (previous attempt sat right behind tier2's front face and was hidden) and
# large enough per-flag to read as individually colored pennants, not a monochrome smear
FLAG_Y = -0.28  # forward of tier1's own face (0.0) and well forward of tier2's face (0.5) — nothing occludes it
FLAG_Z = 2.55
FLAG_X0, FLAG_X1 = -2.35, 2.35
N_FLAGS = 11
for i in range(N_FLAGS):
    t = i / (N_FLAGS - 1)
    fx = FLAG_X0 + (FLAG_X1 - FLAG_X0) * t
    sag = 0.22 * math.sin(t * math.pi)  # slight catenary sag toward the middle
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.3, radius2=0.3, depth=0.035, location=(fx, FLAG_Y, FLAG_Z - sag))
    flag = bpy.context.active_object
    flag.name = f"PrayerFlag_{i}"
    flag.rotation_euler = (math.radians(90), 0, 0)  # tips the flat triangular face to point along -Y, toward the hero camera
    flag.data.materials.append(flag_mats[i % len(flag_mats)])
    dome_parts.append(flag)

# ---------------------------------------------------------------- join, bevel, bake, export
palace = kit.join(marble_parts, "PalaceArchitecture")
kit.bevel(palace, width=0.025, segments=1)
print(f"PalaceArchitecture polys (pre-bake): {len(palace.data.polygons)}")
kit.bake_procedural_to_texture(palace, marble, size=1536, samples=24)

domes = kit.join(dome_parts, "PalaceDomes")

all_objs = [palace, domes, land, lakebed, water]
kit.export_glb(OUT_GLB, objects=all_objs)

tri_count = sum(len(o.data.polygons) for o in all_objs if o.data)
print(f"TOTAL POLY COUNT: {tri_count}")
print(f"Exported: {OUT_GLB}")

# ---------------------------------------------------------------- preview renders
kit.setup_preview_camera_and_light((22, -26, 12), target=(0, 2, 3.5), light_energy=4.5)
kit.render_preview(os.path.join(PREVIEW_DIR, "udaipur_palace_hero.png"), resolution=900, samples=48)

import mathutils
for o in bpy.context.scene.objects:
    if o.type == "CAMERA":
        o.location = (18, 18, 17)
        direction = mathutils.Vector((0, 2, 2.5)) - o.location
        o.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
kit.render_preview(os.path.join(PREVIEW_DIR, "udaipur_palace_iso_angle.png"), resolution=900, samples=48)

print("DONE udaipur_palace.py")

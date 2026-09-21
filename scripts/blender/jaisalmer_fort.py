"""
Builds public/models/jaisalmer_fort.glb — the photoreal hero asset.
Run: /Applications/Blender.app/Contents/MacOS/Blender --background --python jaisalmer_fort.py
"""
import bpy, sys, os, math, random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import rajasthan_kit as kit

PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
OUT_GLB = os.path.join(PROJECT_ROOT, "public", "models", "jaisalmer_fort.glb")
PREVIEW_DIR = os.path.join(PROJECT_ROOT, "public", "models", "previews")

random.seed(42)

kit.clear_scene()

WALL_RADIUS = 7.3
WALL_THICK = 0.55
WALL_HEIGHT = 2.6
WALL_BASE_Z = 1.15  # sits on top of the hill
MERLON_H = 0.42
GATE_GAP_DEG = 26

sandstone = kit.procedural_sandstone_material("Sandstone", base_hex=(0.80, 0.62, 0.34), dark_hex=(0.40, 0.27, 0.15))
rock = kit.flat_material("RockBase", (0.30, 0.24, 0.19), roughness=0.95)
sand_ground = kit.flat_material("SandGround", (0.62, 0.50, 0.33), roughness=0.9)

# ---------------------------------------------------------------- colour accents
door_teal = kit.flat_material("DoorTeal", (0.05, 0.33, 0.32), roughness=0.5)
door_blue = kit.flat_material("DoorBlue", (0.08, 0.20, 0.42), roughness=0.5)
door_red = kit.flat_material("DoorRed", (0.55, 0.10, 0.09), roughness=0.5)
door_mats = [door_red, door_blue, door_teal]
bougain_magenta = kit.flat_material("BougainMagenta", (0.78, 0.12, 0.46), roughness=0.6)
bougain_orange = kit.flat_material("BougainOrange", (0.87, 0.42, 0.08), roughness=0.6)
flag_mats = [
    kit.flat_material("FlagRed", (0.75, 0.12, 0.10)),
    kit.flat_material("FlagBlue", (0.10, 0.25, 0.60)),
    kit.flat_material("FlagYellow", (0.90, 0.70, 0.10)),
    kit.flat_material("FlagGreen", (0.15, 0.55, 0.25)),
    kit.flat_material("FlagWhite", (0.92, 0.90, 0.85)),
]
accent_parts = []

# ---------------------------------------------------------------- hill base
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=8.6, location=(0, 0, -6.6))
hill = bpy.context.active_object
hill.name = "Hill"
hill.scale = (1.0, 1.0, 0.9)
bpy.ops.object.mode_set(mode="EDIT")
import bmesh as _bmesh
bm = _bmesh.from_edit_mesh(hill.data)
to_del = [v for v in bm.verts if v.co.z < -0.3]
_bmesh.ops.delete(bm, geom=to_del, context="VERTS")
_bmesh.update_edit_mesh(hill.data)
bpy.ops.object.mode_set(mode="OBJECT")
mod = hill.modifiers.new("Disp", "DISPLACE")
tex = bpy.data.textures.new("HillNoise", type="CLOUDS")
tex.noise_scale = 1.6
mod.texture = tex
mod.strength = 0.55
bpy.context.view_layer.objects.active = hill
bpy.ops.object.modifier_apply(modifier=mod.name)
hill.data.materials.append(rock)

bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=9.5, depth=0.3, location=(0, 0, -6.75))
ground = bpy.context.active_object
ground.name = "Ground"
ground.data.materials.append(sand_ground)

# ---------------------------------------------------------------- wall ring
arch_parts = []

def polar(radius, angle_deg, z):
    a = math.radians(angle_deg)
    return (radius * math.cos(a), radius * math.sin(a), z)

step = 9
for deg in range(0, 360, step):
    delta = abs(((deg - 180) % 360) - 180)
    if delta < GATE_GAP_DEG:
        continue
    r = WALL_RADIUS + random.uniform(-0.15, 0.15)
    h = WALL_HEIGHT + random.uniform(-0.12, 0.12)
    loc = polar(r, deg, WALL_BASE_Z + h / 2)
    seg = kit.cube(f"Wall_{deg}", (step * 0.021 + 0.05, WALL_THICK, h), loc, material=sandstone)
    seg.rotation_euler[2] = math.radians(deg + 90)
    arch_parts.append(seg)

    mer = kit.cube(f"Merlon_{deg}", (step * 0.013, WALL_THICK * 0.65, MERLON_H), polar(r, deg, WALL_BASE_Z + h + MERLON_H / 2), material=sandstone)
    mer.rotation_euler[2] = math.radians(deg + 90)
    arch_parts.append(mer)

# ---------------------------------------------------------------- bastions
bastion_angles = [22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5]
for i, deg in enumerate(bastion_angles):
    bh = 4.6 if i % 3 != 0 else 5.6
    loc = polar(WALL_RADIUS + 0.15, deg, WALL_BASE_Z + bh / 2)
    tower = kit.cylinder(f"Bastion_{deg}", 1.25, bh, loc, segments=8, material=sandstone, cone_ratio=0.94)
    arch_parts.append(tower)

    band_color = [door_red, door_blue, door_teal, bougain_orange][i % 4]
    band = kit.cylinder(
        f"BastionBand_{deg}", 1.32, bh * 0.4,
        polar(WALL_RADIUS + 0.15, deg, WALL_BASE_Z + bh * 0.58),
        segments=8, material=band_color,
    )
    accent_parts.append(band)
    cap = kit.dome(f"BastionCap_{deg}", 1.35, polar(WALL_RADIUS + 0.15, deg, WALL_BASE_Z + bh), material=sandstone, segments=10, ring_count=5)
    arch_parts.append(cap)
    if i % 3 == 0:
        pillar = kit.cylinder(f"ChhatriPillar_{deg}", 0.28, 1.1, polar(WALL_RADIUS + 0.15, deg, WALL_BASE_Z + bh + 0.55), segments=8, material=sandstone)
        arch_parts.append(pillar)
        chdome = kit.dome(f"ChhatriDome_{deg}", 0.85, polar(WALL_RADIUS + 0.15, deg, WALL_BASE_Z + bh + 1.15), material=sandstone, segments=10, ring_count=5)
        arch_parts.append(chdome)

# ---------------------------------------------------------------- main gate
gate_h = 4.4
gate_loc = polar(WALL_RADIUS, 0, WALL_BASE_Z + gate_h / 2)
gate_body = kit.cube("GateBody", (1.4, WALL_THICK * 2.2, gate_h), gate_loc, material=sandstone)
gate_body.rotation_euler[2] = math.radians(90)

cutter_loc = polar(WALL_RADIUS, 0, WALL_BASE_Z + gate_h * 0.34)
bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1.35, depth=WALL_THICK * 3, location=cutter_loc)
cutter = bpy.context.active_object
cutter.rotation_euler = (math.radians(90), 0, 0)
mod = gate_body.modifiers.new("ArchCut", "BOOLEAN")
mod.operation = "DIFFERENCE"
mod.object = cutter
bpy.context.view_layer.objects.active = gate_body
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cutter, do_unlink=True)
arch_parts.append(gate_body)

for side in (-1, 1):
    fdeg = side * 14
    fh = 6.2
    fl = polar(WALL_RADIUS + 0.1, fdeg, WALL_BASE_Z + fh / 2)
    flank = kit.cylinder(f"GateFlank_{side}", 1.05, fh, fl, segments=8, material=sandstone, cone_ratio=0.9)
    arch_parts.append(flank)
    fcap = kit.dome(f"GateFlankCap_{side}", 1.15, polar(WALL_RADIUS + 0.1, fdeg, WALL_BASE_Z + fh), material=sandstone, segments=10, ring_count=5)
    arch_parts.append(fcap)

gate_chhatri_pillar = kit.cylinder("GateChhatriPillar", 0.32, 1.2, polar(WALL_RADIUS, 0, WALL_BASE_Z + gate_h + 0.6), segments=8, material=sandstone)
arch_parts.append(gate_chhatri_pillar)
gate_chhatri_dome = kit.dome("GateChhatriDome", 0.95, polar(WALL_RADIUS, 0, WALL_BASE_Z + gate_h + 1.25), material=sandstone, segments=12, ring_count=6)
arch_parts.append(gate_chhatri_dome)

# ---------------------------------------------------------------- interior havelis
for i in range(16):
    deg = random.uniform(0, 360)
    r = random.uniform(1.0, WALL_RADIUS - 1.3)
    h = random.uniform(2.4, 6.3)
    w = random.uniform(1.1, 2.1)
    d = random.uniform(1.1, 2.1)
    loc = polar(r, deg, WALL_BASE_Z + h / 2 - 0.3)
    bld = kit.cube(f"Haveli_{i}", (w, d, h), loc, material=sandstone)
    bld.rotation_euler[2] = math.radians(random.uniform(0, 90))
    arch_parts.append(bld)

    if i % 4 == 0:
        door_mat = door_mats[(i // 4) % len(door_mats)]
        plaque = kit.cube(
            f"HaveliDoor_{i}",
            (w * 0.4, d * 1.05, h * 0.3),
            (loc[0], loc[1], loc[2] - h * 0.28),
            material=door_mat,
        )
        plaque.rotation_euler[2] = bld.rotation_euler[2]
        accent_parts.append(plaque)

# ---------------------------------------------------------------- gate door (full leaf, near arch-width)
door_h = gate_h * 0.68
door_loc = polar(WALL_RADIUS + 0.08, 0, WALL_BASE_Z + door_h / 2)
gate_door = kit.cube("GateDoor", (0.16, 2.6, door_h), door_loc, material=door_teal)
gate_door.rotation_euler[2] = math.radians(90)
accent_parts.append(gate_door)

# ---------------------------------------------------------------- gate awning / canopy (large color block)
awning_mat = kit.flat_material("Awning", (0.62, 0.10, 0.10), roughness=0.55)
awning_loc = polar(WALL_RADIUS + 0.55, 0, WALL_BASE_Z + gate_h * 0.92)
awning = kit.cube("GateAwning", (0.14, 3.0, 1.15), awning_loc, material=awning_mat)
awning.rotation_euler[2] = math.radians(90)
awning.rotation_euler[0] = math.radians(-16)
accent_parts.append(awning)

# ---------------------------------------------------------------- painted rampart band (large color block) —
# runs the FULL wall circumference (same gate-gap exclusion as the wall ring itself) so it reads from any angle
band_mat = kit.flat_material("RampartBand", (0.70, 0.18, 0.09), roughness=0.5)
for deg in range(0, 360, step):
    delta = abs(((deg - 180) % 360) - 180)
    if delta < GATE_GAP_DEG:
        continue
    r = WALL_RADIUS + 0.1
    bh = WALL_HEIGHT * 0.48
    seg = kit.cube(f"Band_{deg}", (step * 0.022 + 0.07, WALL_THICK * 0.6, bh), polar(r, deg, WALL_BASE_Z + bh / 2 + 0.08), material=band_mat)
    seg.rotation_euler[2] = math.radians(deg + 90)
    accent_parts.append(seg)

# ---------------------------------------------------------------- bougainvillea clusters — bigger, spread wide
bougain_centers = [
    (-140, bougain_magenta), (-80, bougain_orange), (-20, bougain_magenta),
    (100, bougain_orange), (160, bougain_magenta), (220, bougain_orange),
]
for deg, mat in bougain_centers:
    for j in range(5):
        offset = random.uniform(-14, 14)
        radius_b = random.uniform(0.45, 0.78)
        bloom = kit.dome(
            f"Bougain_{deg}_{j}",
            radius_b,
            polar(WALL_RADIUS + 0.25, deg + offset, WALL_BASE_Z + random.uniform(0.5, 2.3)),
            material=mat,
            segments=8,
            ring_count=4,
        )
        accent_parts.append(bloom)

# ---------------------------------------------------------------- prayer flag bunting — scaled up
flag_start_deg, flag_end_deg = 15, 75
flag_count = 11
for k in range(flag_count):
    t = k / (flag_count - 1)
    deg = flag_start_deg + (flag_end_deg - flag_start_deg) * t
    sag = math.sin(t * math.pi) * 0.5
    z = WALL_BASE_Z + WALL_HEIGHT + 1.1 - sag
    fmat = flag_mats[k % len(flag_mats)]
    flag = kit.cylinder(f"Flag_{k}", 0.35, 0.06, polar(WALL_RADIUS + 0.15, deg, z), segments=3, material=fmat, cone_ratio=0.05)
    flag.rotation_euler[0] = math.radians(90)
    accent_parts.append(flag)

# ---------------------------------------------------------------- join, bevel, bake, export
fort = kit.join(arch_parts, "FortArchitecture")
kit.bevel(fort, width=0.025, segments=1)

print(f"FortArchitecture tris (pre-bake): {len(fort.data.polygons)} polys")

kit.bake_procedural_to_texture(fort, sandstone, size=1536, samples=24)

all_objs = [fort, hill, ground] + accent_parts
kit.export_glb(OUT_GLB, objects=all_objs)

tri_count = sum(len(o.data.polygons) for o in all_objs if o.data)
print(f"TOTAL POLY COUNT: {tri_count}")
print(f"Exported: {OUT_GLB}")

# ---------------------------------------------------------------- preview renders
kit.setup_preview_camera_and_light((24, -27, 12), target=(0, 0, 2.5), light_energy=4.5)
kit.render_preview(os.path.join(PREVIEW_DIR, "jaisalmer_fort_hero.png"), resolution=900, samples=48)

for o in bpy.context.scene.objects:
    if o.type == "CAMERA":
        o.location = (18, 18, 17)
        import mathutils
        direction = mathutils.Vector((0, 0, 1.5)) - o.location
        o.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
kit.render_preview(os.path.join(PREVIEW_DIR, "jaisalmer_fort_iso_angle.png"), resolution=900, samples=48)

print("DONE jaisalmer_fort.py")

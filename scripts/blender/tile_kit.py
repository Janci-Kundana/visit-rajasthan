"""
Shared builder for the isometric destination tiles.

Every destination tile is a thick slab with a road layout on top and a cluster of
that city's recognisable landmarks standing on it — the "diorama on a chip" look.

Design constraints that drove this file:

  * Flat Principled materials only, no image textures. Four of these load live in
    the browser at once, so each .glb has to stay small; untextured flat materials
    keep a full tile around 150-300 KB instead of the 1-2 MB the older baked-
    texture builds produced.
  * Everything is joined per-tile before export. glTF emits one mesh with several
    material slots, which is a handful of draw calls rather than a few hundred.
  * The tile is authored Z-up around the origin with its top face at z = 0, so the
    web side can drop it straight in without hunting for an offset.

Run headlessly:
  /Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/blender/<city>_tile.py
"""
import bpy
import bmesh
import math
import os
import random

TAU = math.pi * 2

# Tile footprint. Landmarks are placed in this coordinate space.
TILE_X = 12.0
TILE_Y = 12.0
TILE_H = 1.15          # slab thickness
GROUND_Z = 0.0         # top face of the slab


# --------------------------------------------------------------------------
# scene plumbing
# --------------------------------------------------------------------------

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images,
                 bpy.data.cameras, bpy.data.lights, bpy.data.curves):
        for block in list(coll):
            if block.users == 0:
                coll.remove(block)


def srgb_to_linear(c):
    """Blender (and glTF's baseColorFactor) store base colour in LINEAR space.

    Palettes here are picked by eye as sRGB — the values you'd type into CSS — so
    they have to be converted or everything renders a washed-out pastel. This bit
    us on the first build: the whole tile looked chalky until the conversion went
    in. It matters for the exported .glb too, not just the preview render.
    """
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def mat(name, color, roughness=0.62, metallic=0.0):
    """Flat Principled material from an sRGB colour. Reused by name so the
    exporter emits one material slot rather than one per call."""
    existing = bpy.data.materials.get(name)
    if existing:
        return existing
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    lin = tuple(srgb_to_linear(c) for c in color)
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*lin, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return m


def glass(name, color, roughness=0.12):
    return mat(name, color, roughness=roughness, metallic=0.35)


def _finish(obj, material, smooth=False):
    if material:
        obj.data.materials.append(material)
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def _apply(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


# --------------------------------------------------------------------------
# primitives
# --------------------------------------------------------------------------

def box(name, center, dims, material=None, rot_z=0.0):
    """Axis-aligned box; `dims` is full width/depth/height, `center` its centre."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    o = bpy.context.active_object
    o.name = name
    o.scale = dims
    o.rotation_euler.z = rot_z
    _apply(o)
    return _finish(o, material)


def slab_on_ground(name, center_xy, dims_xy, height, material=None, rot_z=0.0, z0=GROUND_Z):
    """Box that sits ON the ground plane rather than being centred on it."""
    return box(name,
               (center_xy[0], center_xy[1], z0 + height / 2.0),
               (dims_xy[0], dims_xy[1], height),
               material, rot_z)


def cyl(name, center, radius, height, material=None, verts=20, smooth=True):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius,
                                        depth=height, location=center)
    o = bpy.context.active_object
    o.name = name
    return _finish(o, material, smooth)


def cone(name, center, r1, r2, height, material=None, verts=20, smooth=True):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2,
                                    depth=height, location=center)
    o = bpy.context.active_object
    o.name = name
    return _finish(o, material, smooth)


def dome(name, center, radius, material=None, segments=18, rings=9, squash=1.0):
    """Upper hemisphere; `squash` > 1 makes the onion/bulb profile."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings,
                                         radius=radius, location=center)
    o = bpy.context.active_object
    o.name = name
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(o.data)
    doomed = [v for v in bm.verts if v.co.z < -0.001]
    bmesh.ops.delete(bm, geom=doomed, context="VERTS")
    bmesh.update_edit_mesh(o.data)
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.fill_holes(sides=0)
    bpy.ops.object.mode_set(mode="OBJECT")
    if squash != 1.0:
        o.scale = (1, 1, squash)
        _apply(o)
    return _finish(o, material, smooth=True)


def onion_dome(name, base_center, radius, material, finial_mat=None, height_scale=1.35):
    """Bulbous Mughal/Rajput dome with a neck and finial — the motif that reads
    'Rajasthan' at thumbnail size more than any other."""
    parts = []
    parts.append(cyl(f"{name}_drum", (base_center[0], base_center[1], base_center[2] + radius * 0.16),
                     radius * 0.92, radius * 0.32, material, verts=18))
    d = dome(f"{name}_bulb", (base_center[0], base_center[1], base_center[2] + radius * 0.3),
             radius, material, squash=height_scale)
    parts.append(d)
    parts.append(cone(f"{name}_finial",
                      (base_center[0], base_center[1], base_center[2] + radius * (0.3 + height_scale) + radius * 0.16),
                      radius * 0.1, 0.0, radius * 0.42, finial_mat or material, verts=8))
    return parts


def chhatri(name, center, pillar_h, radius, stone, dome_mat=None):
    """The open domed pavilion on every Rajasthani roofline."""
    parts = []
    for i in range(6):
        a = TAU * i / 6.0
        parts.append(cyl(f"{name}_p{i}",
                         (center[0] + math.cos(a) * radius, center[1] + math.sin(a) * radius,
                          center[2] + pillar_h / 2.0),
                         radius * 0.12, pillar_h, stone, verts=6))
    parts.append(cyl(f"{name}_slab", (center[0], center[1], center[2] + pillar_h + 0.045),
                     radius * 1.3, 0.09, stone, verts=12))
    parts += onion_dome(f"{name}_dome",
                        (center[0], center[1], center[2] + pillar_h + 0.09),
                        radius * 0.78, dome_mat or stone, height_scale=1.15)
    return parts


def crenellation(name, start, end, z, stone, merlon=0.16, gap=0.2, height=0.24):
    """Battlement teeth along a wall run — reads as 'fort' instantly."""
    parts = []
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    if length < 1e-6:
        return parts
    ux, uy = dx / length, dy / length
    step = merlon + gap
    n = max(1, int(length / step))
    for i in range(n):
        t = (i + 0.5) * step
        if t > length:
            break
        parts.append(box(f"{name}_m{i}",
                         (start[0] + ux * t, start[1] + uy * t, z + height / 2.0),
                         (merlon, merlon, height), stone,
                         rot_z=math.atan2(uy, ux)))
    return parts


def window_grid(name, face_center, normal, width, height, rows, cols, glass_mat,
                inset=0.03, pad=0.16):
    """Punches a grid of window quads slightly proud of a facade."""
    parts = []
    nx, ny = normal
    # in-plane horizontal axis
    hx, hy = -ny, nx
    cw = (width - pad * 2) / cols
    ch = (height - pad * 2) / rows
    for r in range(rows):
        for c in range(cols):
            ox = -width / 2 + pad + cw * (c + 0.5)
            oz = -height / 2 + pad + ch * (r + 0.5)
            parts.append(box(f"{name}_{r}_{c}",
                             (face_center[0] + hx * ox + nx * inset,
                              face_center[1] + hy * ox + ny * inset,
                              face_center[2] + oz),
                             (abs(hx) * cw * 0.72 + abs(nx) * 0.02,
                              abs(hy) * cw * 0.72 + abs(ny) * 0.02,
                              ch * 0.62),
                             glass_mat))
    return parts


# --------------------------------------------------------------------------
# tile furniture
# --------------------------------------------------------------------------

def base_slab(top_mat, side_mat, x=TILE_X, y=TILE_Y, h=TILE_H):
    """The chip the diorama sits on: ground plate + thicker skirt below it, so the
    top surface and the cut-earth sides can take different colours."""
    top = box("tile_top", (0, 0, GROUND_Z - 0.06), (x, y, 0.12), top_mat)
    skirt = box("tile_skirt", (0, 0, GROUND_Z - 0.12 - (h - 0.12) / 2.0),
                (x * 0.995, y * 0.995, h - 0.12), side_mat)
    m = skirt.modifiers.new("Bevel", "BEVEL")
    m.width = 0.05
    m.segments = 2
    bpy.context.view_layer.objects.active = skirt
    bpy.ops.object.modifier_apply(modifier=m.name)
    return [top, skirt]


def road(name, start, end, width, asphalt, marking_mat, dashed=True, z=GROUND_Z,
         layer=0, skip=None):
    """Road strip laid flush on the ground, with a dashed centre line.

    `layer` lifts the bed by a hair so crossing roads never z-fight (the giveaway
    is a black square at the junction). `skip` is a list of (x, y, radius) points
    — usually the junctions — where the centre line is omitted, which is both how
    real road markings work and what stops dashes stacking at a crossing.
    """
    parts = []
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    ang = math.atan2(dy, dx)
    cx, cy = (start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0
    bed_z = z + 0.014 + layer * 0.006
    parts.append(box(f"{name}_bed", (cx, cy, bed_z), (length, width, 0.028 + layer * 0.006),
                     asphalt, rot_z=ang))
    if dashed and marking_mat:
        n = max(1, int(length / 0.85))
        for i in range(n):
            t = -length / 2 + (i + 0.5) * (length / n)
            px = cx + math.cos(ang) * t
            py = cy + math.sin(ang) * t
            if skip and any(math.hypot(px - sx, py - sy) < sr for sx, sy, sr in skip):
                continue
            parts.append(box(f"{name}_d{i}", (px, py, bed_z + 0.021),
                             (length / n * 0.44, width * 0.05, 0.01),
                             marking_mat, rot_z=ang))
    return parts


def kerb(name, start, end, width, kerb_mat, z=GROUND_Z, thickness=0.09):
    """Pale pavement edging either side of a road run — the detail that makes the
    asphalt read as a street rather than a grey rectangle."""
    parts = []
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    ang = math.atan2(dy, dx)
    cx, cy = (start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0
    nx, ny = -math.sin(ang), math.cos(ang)
    for sgn in (-1, 1):
        off = sgn * (width / 2.0 + thickness / 2.0)
        parts.append(box(f"{name}_k{sgn}", (cx + nx * off, cy + ny * off, z + 0.032),
                         (length, thickness, 0.064), kerb_mat, rot_z=ang))
    return parts


def car(name, pos, ang, body_mat, glass_mat):
    parts = []
    parts.append(box(f"{name}_body", (pos[0], pos[1], GROUND_Z + 0.105),
                     (0.46, 0.22, 0.15), body_mat, rot_z=ang))
    parts.append(box(f"{name}_cab", (pos[0], pos[1], GROUND_Z + 0.205),
                     (0.24, 0.195, 0.1), glass_mat, rot_z=ang))
    return parts


def tree(name, pos, scale=1.0, trunk_mat=None, leaf_mat=None, kind="round"):
    parts = []
    h = 0.34 * scale
    parts.append(cyl(f"{name}_trunk", (pos[0], pos[1], GROUND_Z + h / 2.0),
                     0.045 * scale, h, trunk_mat, verts=6))
    if kind == "round":
        parts.append(dome(f"{name}_crown", (pos[0], pos[1], GROUND_Z + h * 0.92),
                          0.27 * scale, leaf_mat, segments=12, rings=7, squash=1.5))
    elif kind == "palm":
        for i in range(6):
            a = TAU * i / 6.0
            parts.append(box(f"{name}_frond{i}",
                             (pos[0] + math.cos(a) * 0.17 * scale,
                              pos[1] + math.sin(a) * 0.17 * scale,
                              GROUND_Z + h + 0.03 * scale),
                             (0.34 * scale, 0.07 * scale, 0.035 * scale),
                             leaf_mat, rot_z=a))
    else:  # scrub / thorn — dry Rajasthan roadside
        for i in range(3):
            a = TAU * i / 3.0 + 0.4
            parts.append(dome(f"{name}_c{i}",
                              (pos[0] + math.cos(a) * 0.1 * scale,
                               pos[1] + math.sin(a) * 0.1 * scale,
                               GROUND_Z + h * 0.8),
                              0.16 * scale, leaf_mat, segments=8, rings=5, squash=0.85))
    return parts


def water_patch(name, center, dims, water_mat, bank_mat=None, z=GROUND_Z, bank=0.16):
    """Water laid ON the ground plate, ringed by a slightly raised bank.

    Genuinely recessing the water would mean boolean-cutting the ground plate for
    every lake; ringing it with a raised bank sells the same read for a fraction
    of the geometry, and the bank doubles as the ghat/shoreline edge.
    """
    parts = []
    if bank_mat:
        parts.append(box(f"{name}_bank", (center[0], center[1], z + 0.028),
                         (dims[0] + bank * 2, dims[1] + bank * 2, 0.056), bank_mat))
    parts.append(box(name, (center[0], center[1], z + 0.036),
                     (dims[0], dims[1], 0.05), water_mat))
    return parts


def water_disc(name, center, radius, water_mat, bank_mat=None, z=GROUND_Z, bank=0.18, verts=28):
    """Round-edged variant for natural lakes and reservoirs."""
    parts = []
    if bank_mat:
        parts.append(cyl(f"{name}_bank", (center[0], center[1], z + 0.028),
                         radius + bank, 0.056, bank_mat, verts=verts, smooth=False))
    parts.append(cyl(name, (center[0], center[1], z + 0.036), radius, 0.05,
                     water_mat, verts=verts, smooth=False))
    return parts


def rock(name, pos, radius, rock_mat, seed=0, squash=0.72):
    """Weathered granite boulder — Jawai's whole identity."""
    rnd = random.Random(seed)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius,
                                          location=(pos[0], pos[1], pos[2]))
    o = bpy.context.active_object
    o.name = name
    for v in o.data.vertices:
        v.co.x += rnd.uniform(-0.09, 0.09) * radius
        v.co.y += rnd.uniform(-0.09, 0.09) * radius
        v.co.z += rnd.uniform(-0.07, 0.07) * radius
    o.scale = (1.0, 0.92, squash)
    _apply(o)
    return _finish(o, rock_mat, smooth=True)


# --------------------------------------------------------------------------
# assembly / export
# --------------------------------------------------------------------------

def join_all(objects, name):
    objects = [o for o in objects if o is not None]
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    result = bpy.context.active_object
    result.name = name
    # Centre the tile on the origin so the web side needs no magic offsets.
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    result.location = (0, 0, 0)
    return result


def export_glb(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
        export_yup=True,
    )
    print(f"[tile_kit] exported {path}")


def setup_iso_render(target=(0, 0, 0), span=9.2, sun_energy=4.2, bg=(0.87, 0.92, 0.97)):
    """Orthographic three-quarter camera matching the framing the site uses."""
    cam_data = bpy.data.cameras.new("IsoCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = span
    cam = bpy.data.objects.new("IsoCam", cam_data)
    bpy.context.collection.objects.link(cam)

    el, dist = math.radians(35.264), 30.0
    cam.location = (target[0] + dist * 0.5774, target[1] - dist * 0.5774, target[2] + dist * 0.5774)
    cam.rotation_euler = (math.radians(54.736), 0, math.radians(45))
    bpy.context.scene.camera = cam

    sun_data = bpy.data.lights.new("Sun", type="SUN")
    sun_data.energy = sun_energy
    sun_data.angle = math.radians(4.5)      # soft-edged contact shadows
    sun = bpy.data.objects.new("Sun", sun_data)
    bpy.context.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(42), math.radians(6), math.radians(28))

    # Low ambient so the flat colours keep their punch; the sun does the modelling.
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bgn = world.node_tree.nodes.get("Background")
    if bgn:
        bgn.inputs["Color"].default_value = (*bg, 1)
        bgn.inputs["Strength"].default_value = 0.55
    return cam


def render_preview(path, resolution=880, samples=64, transparent=False):
    """`transparent=True` renders the poster used as the card's fallback image
    before the .glb loads (and on devices where WebGL is unavailable), so it has
    to sit on whatever card background the site uses."""
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    try:
        scene.cycles.device = "CPU"
    except Exception:
        pass
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.film_transparent = transparent
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    scene.render.filepath = path

    # Blender 4.x defaults to the AgX view transform, which desaturates hard and
    # makes these flat colours look chalky and grey. The preview exists to judge
    # the palette that will ship in the .glb, so render it straight.
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0

    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    print(f"[tile_kit] rendered {path}")

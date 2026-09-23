"""
Shared builder for the isometric destination tiles.

Every destination tile is a thick slab with a road layout on top and a cluster of
that city's recognisable landmarks standing on it — the "diorama on a chip" look.

Design constraints that drove this file:

  * Physically based image materials travel with the GLB. Stone, plaster, water,
    timber and foliage carry albedo, roughness and normal detail in the browser.
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
from mathutils import Vector
from tile_surfaces import material as surface_material, prepare as prepare_surfaces, save_source

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
    return surface_material(name, color, roughness, metallic)


def glass(name, color, roughness=0.12):
    return mat(name, tuple(c * .42 for c in color), roughness=roughness, metallic=0.1)


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
    vertices = [(x * dims[0] / 2, y * dims[1] / 2, z * dims[2] / 2)
                for z in (-1, 1) for y in (-1, 1) for x in (-1, 1)]
    faces = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4),
             (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    o = mesh_object(name, vertices, faces)
    o.location = center
    o.rotation_euler.z = rot_z
    # Real edges catch a highlight. Keep editable corners for the two ramps.
    if min(dims) > .025 and "gnomon" not in name and "ramp" not in name:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=min(.012, min(dims) * .12), segments=2, affect="EDGES")
        bm.to_mesh(o.data)
        bm.free()
        o.data.update()
    return _finish(o, material)


def mesh_object(name, vertices, faces, material=None, smooth=False):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return _finish(obj, material, smooth)


def ellipsoid(name, pos, dims, material, angle=0, detail=2):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=detail, radius=1)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = pos
    obj.scale = dims
    obj.rotation_euler.z = angle
    return _finish(obj, material, True)


def rod(name, start, end, radius, material, vertices=8):
    a, b = Vector(start), Vector(end)
    obj = cyl(name, (a + b) / 2, radius, (b - a).length, material, verts=vertices)
    obj.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
    return obj


def tube(name, points, radius, material, sides=6):
    vertices, faces = [], []
    for i, point in enumerate(points):
        tangent = Vector(points[min(i + 1, len(points) - 1)]) - Vector(points[max(0, i - 1)])
        tangent.normalize()
        normal = tangent.cross(Vector((0, 0, 1)))
        if normal.length < .01:
            normal = tangent.cross(Vector((0, 1, 0)))
        normal.normalize()
        second = tangent.cross(normal)
        for j in range(sides):
            v = Vector(point) + radius * (math.cos(TAU * j / sides) * normal + math.sin(TAU * j / sides) * second)
            vertices.append(tuple(v))
        if i:
            for j in range(sides):
                a, b = (i - 1) * sides + j, (i - 1) * sides + (j + 1) % sides
                faces.append((a, b, b + sides, a + sides))
    faces += [tuple(reversed(range(sides))), tuple(range(len(vertices) - sides, len(vertices)))]
    return mesh_object(name, vertices, faces, material, True)


def arch_window(name, center, normal, width, height, stone, lattice=False):
    """Dark arched reveal behind a carved stone frame, sill and optional jali."""
    nx, ny = normal
    hx, hy = -ny, nx
    def point(x, z, depth):
        return (center[0] + hx * x + nx * depth, center[1] + hy * x + ny * depth, center[2] + z)
    dark = mat("recess_shadow", (.145, .112, .083), .9)
    radius = width / 2
    spring = height / 2 - radius
    outline = [(-radius, -height / 2), (radius, -height / 2)]
    outline += [(radius * math.cos(a), spring + radius * math.sin(a)) for a in [math.pi * j / 12 for j in range(13)]]
    pane = mesh_object(name + "_reveal", [point(x, z, .013) for x, z in outline], [tuple(range(len(outline)))], dark)
    parts = [pane]
    # A continuous moulding creates real relief and a shadow around the opening.
    profile = [point(x, z, .037) for x, z in outline[1:]] + [point(-radius, -height / 2, .037)]
    parts.append(tube(name + "_arch", profile, min(width * .07, .017), stone))
    parts.append(box(name + "_sill", point(0, -height / 2 - .018, .045), (width * 1.20, .10, .035), stone, math.atan2(hy, hx)))
    if lattice and height > .08:
        for i in (-1, 0, 1):
            xx = i * width * .22
            parts.append(rod(name + "_jali", point(xx, -height * .42, .023), point(xx, spring + math.sqrt(max(0, radius ** 2 - xx ** 2)) - .02, .023), .006, stone, 4))
        for fraction in (-.22, .08):
            parts.append(rod(name + "_cross", point(-width * .43, height * fraction, .025), point(width * .43, height * fraction, .025), .006, stone, 4))
    return parts


def slab_on_ground(name, center_xy, dims_xy, height, material=None, rot_z=0.0, z0=GROUND_Z):
    """Box that sits ON the ground plane rather than being centred on it."""
    return box(name,
               (center_xy[0], center_xy[1], z0 + height / 2.0),
               (dims_xy[0], dims_xy[1], height),
               material, rot_z)


def cyl(name, center, radius, height, material=None, verts=20, smooth=True):
    return cone(name, center, radius, radius, height, material, verts, smooth)


def cone(name, center, r1, r2, height, material=None, verts=20, smooth=True):
    vertices = [(r * math.cos(TAU * i / verts), r * math.sin(TAU * i / verts), z)
                for r, z in ((r1, -height / 2), (r2, height / 2)) for i in range(verts)]
    faces = [tuple(reversed(range(verts))), tuple(range(verts, 2 * verts))]
    faces += [(i, (i + 1) % verts, (i + 1) % verts + verts, i + verts) for i in range(verts)]
    obj = mesh_object(name, vertices, faces, material)
    obj.location = center
    if smooth:
        for p in list(obj.data.polygons)[2:]:
            p.use_smooth = True
    return obj


def dome(name, center, radius, material=None, segments=18, rings=9, squash=1.0):
    profile = [(radius * max(.001, math.cos(math.pi * .5 * i / rings)),
                radius * squash * math.sin(math.pi * .5 * i / rings)) for i in range(rings + 1)]
    return lathe(name, center, profile, material, max(24, segments))


def lathe(name, center, profile, material, segments=32):
    verts = [(center[0] + r * math.cos(TAU * i / segments), center[1] + r * math.sin(TAU * i / segments), center[2] + z)
             for r, z in profile for i in range(segments)]
    faces = [(j * segments + i, j * segments + (i + 1) % segments,
              (j + 1) * segments + (i + 1) % segments, (j + 1) * segments + i)
             for j in range(len(profile) - 1) for i in range(segments)]
    faces += [tuple(reversed(range(segments))), tuple(range(len(verts) - segments, len(verts)))]
    return mesh_object(name, verts, faces, material, True)


def onion_dome(name, base_center, radius, material, finial_mat=None, height_scale=1.35):
    """Bulbous Mughal/Rajput dome with a neck and finial — the motif that reads
    'Rajasthan' at thumbnail size more than any other."""
    parts = []
    parts.append(cyl(f"{name}_drum", (base_center[0], base_center[1], base_center[2] + radius * 0.16),
                     radius * 0.92, radius * 0.32, material, verts=18))
    profile = [(.72, 0), (.86, .12), (.98, .30), (1, .45), (.93, .63), (.77, .80), (.49, .96), (.19, 1.11), (.045, 1.26)]
    d = lathe(f"{name}_bulb", (base_center[0], base_center[1], base_center[2] + radius * .3),
              [(r * radius, z * radius * height_scale / 1.26) for r, z in profile], material)
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
    for i in range(6):
        a = TAU * i / 6
        x, y = center[0] + math.cos(a) * radius, center[1] + math.sin(a) * radius
        parts.append(cyl(f"{name}_capital{i}", (x, y, center[2] + pillar_h - .015), radius * .21, .055, stone, verts=8))
        parts.append(cyl(f"{name}_foot{i}", (x, y, center[2] + .022), radius * .18, .044, stone, verts=8))
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
            parts += arch_window(f"{name}_{r}_{c}",
                                 (face_center[0] + hx * ox + nx * inset,
                                  face_center[1] + hy * ox + ny * inset, face_center[2] + oz),
                                 normal, cw * .65, max(.055, ch * .83), glass_mat, lattice=True)
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
    def p(x, y, z):
        return (pos[0] + math.cos(ang) * x - math.sin(ang) * y,
                pos[1] + math.sin(ang) * x + math.cos(ang) * y, z)
    rubber = mat("tyre_rubber", (.055, .055, .052), .92)
    chrome = mat("car_chrome", (.55, .57, .58), .23, .85)
    headlamp = mat("car_headlight", (.95, .92, .78), .18)
    tail = mat("car_tail_light", (.48, .025, .012), .25)
    parts = [box(name + "_body", p(0, 0, .14), (.50, .23, .13), body_mat, ang),
             box(name + "_windows", p(-.025, 0, .235), (.26, .20, .10), glass_mat, ang),
             box(name + "_roof", p(-.025, 0, .29), (.23, .20, .025), body_mat, ang)]
    for x in (-.15, .16):
        for y in (-.12, .12):
            parts.append(rod(name + "_tyre", p(x, y - .018, .095), p(x, y + .018, .095), .063, rubber, 16))
            parts.append(rod(name + "_hub", p(x, y - .020, .095), p(x, y + .020, .095), .031, chrome, 12))
    for y in (-.072, .072):
        parts.append(box(name + "_headlight", p(.252, y, .17), (.012, .057, .033), headlamp, ang))
        parts.append(box(name + "_tail", p(-.252, y, .17), (.012, .050, .028), tail, ang))
    for x in (-.257, .257):
        parts.append(box(name + "_bumper", p(x, 0, .10), (.025, .225, .026), chrome, ang))
    for y in (-.103, .103):
        parts.append(box(name + "_pillar", p(-.03, y, .24), (.021, .013, .10), body_mat, ang))
    return parts


def tree(name, pos, scale=1.0, trunk_mat=None, leaf_mat=None, kind="round"):
    rng = random.Random(name)
    h = (.83 if kind == "palm" else .48) * scale
    x, y = pos
    parts = [cone(name + "_trunk", (x, y, h / 2), .035 * scale, .020 * scale, h, trunk_mat, 9)]
    if kind == "palm":
        for i in range(9):
            a = TAU * i / 9 + .23
            points = [(x + math.cos(a) * t * .53 * scale,
                       y + math.sin(a) * t * .53 * scale,
                       h + (.18 * math.sin(t * math.pi) - .17 * t) * scale) for t in (0, .2, .4, .6, .8, 1)]
            parts.append(tube(name + "_frond_stem", points, .008 * scale, trunk_mat, 4))
            for j in range(1, 5):
                px, py, pz = points[j]
                for side in (-1, 1):
                    tip = (px + math.cos(a + side * .8) * .14 * scale,
                           py + math.sin(a + side * .8) * .14 * scale, pz - .075 * scale)
                    parts.append(mesh_object(name + "_leaflet", [(px, py, pz), (px - math.sin(a) * .05 * scale, py + math.cos(a) * .05 * scale, pz + .006), tip], [(0, 1, 2)], leaf_mat))
    else:
        count = 13 if kind == "round" else 9
        for i in range(count):
            a = rng.uniform(0, TAU)
            r = rng.uniform(.04, .27) * scale
            px, py = x + math.cos(a) * r, y + math.sin(a) * r
            z = h + rng.uniform(-.04, .16) * scale
            if kind == "scrub":
                z = h + rng.uniform(-.08, .035) * scale
            parts.append(rod(name + "_branch", (x, y, h * .55), (px, py, z), .011 * scale, trunk_mat, 5))
            parts.append(ellipsoid(name + "_foliage", (px, py, z), (.14 * scale, .13 * scale, (.18 if kind == "round" else .085) * scale), leaf_mat, a))
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
    # Fine, irregular wave geometry supplies a real specular silhouette as well
    # as the exported normal map. Keep the amplitude below the shoreline.
    nx, ny = max(8, int(dims[0] * 12)), max(8, int(dims[1] * 12))
    verts = []
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = center[0] + dims[0] * (i / nx - .5)
            y = center[1] + dims[1] * (j / ny - .5)
            wave = .002 * math.sin(5 * y + 1.2 * x) + .001 * math.sin(7 * x - 3 * y)
            verts.append((x, y, z + .067 + wave))
    faces = [(j * (nx + 1) + i, j * (nx + 1) + i + 1,
              (j + 1) * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i)
             for j in range(ny) for i in range(nx)]
    parts.append(mesh_object(name, verts, faces, water_mat, True))
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
    o = ellipsoid(name, pos, (1, 1, 1), None, detail=4)
    for v in o.data.vertices:
        x, y, z = v.co
        distortion = 1 + .075 * math.sin(x * 7 + seed) * math.sin(y * 5 - z * 4) + .025 * math.cos(z * 16 + y * 8)
        v.co *= radius * distortion
    o.scale = (1.0, 0.92, squash)
    _apply(o)
    return _finish(o, rock_mat, smooth=True)


# --------------------------------------------------------------------------
# assembly / export
# --------------------------------------------------------------------------

def join_all(objects, name):
    objects = [o for o in objects if o is not None]
    prepare_surfaces(objects)
    # Retain individual parts in the .blend saved after the poster render.
    source_collection = bpy.data.collections.new("Editable landmarks")
    bpy.context.scene.collection.children.link(source_collection)
    for obj in objects:
        source_collection.objects.link(obj)
    source_collection.hide_render = True
    source_collection.hide_viewport = True
    # Duplicate only the objects; joined export data is independent of source data.
    copies = []
    for obj in objects:
        copy = obj.copy()
        copy.data = obj.data.copy()
        bpy.context.scene.collection.objects.link(copy)
        copies.append(copy)
        for coll in list(obj.users_collection):
            if coll != source_collection:
                coll.objects.unlink(obj)
    objects = copies
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    result = bpy.context.active_object
    result.name = name
    result.data.validate(verbose=True)
    result.data.update()
    # Centre the tile on the origin so the web side needs no magic offsets.
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    return result


def export_glb(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    # Explicit triangles let Blender export portable tangent-space normals.
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=list(bm.edges))
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    collapsed = [f for f in bm.faces if f.calc_area() < 1e-8]
    if collapsed:
        bmesh.ops.delete(bm, geom=collapsed, context="FACES_ONLY")
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    # Project the final transformed triangles, including newly beveled faces,
    # so every exported tangent has a non-degenerate UV basis.
    prepare_surfaces([obj])
    # Blender 5.2's meshopt exporter applies a fixed 12-bit exponential filter
    # to positions/normals without updating accessor bounds. It also collapses
    # thin relief. Use its lossless attribute path for these miniature models.
    # This override is scoped to this export; no installed Blender files change.
    from io_scene_gltf2.io.exp import meshopt
    import numpy as np
    encode = meshopt.MeshoptEncoder.encode_attribute
    normals = None
    def encode_exact(name, data, stride, settings):
        nonlocal normals
        if name == "NORMAL":
            normals = data
        elif name == "TANGENT":
            bad = np.linalg.norm(data[:, :3], axis=1) < .5
            if np.any(bad):
                # MikkTSpace can emit zero vectors on very long, thin bevel
                # triangles. Construct an orthogonal basis from their normals.
                if normals is None or len(normals) != len(data):
                    raise RuntimeError("Cannot repair tangent without matching normals")
                n = normals[bad]
                axis = np.eye(3)[np.argmin(np.abs(n), axis=1)]
                tangent = axis - n * np.sum(axis * n, axis=1)[:, None]
                tangent /= np.linalg.norm(tangent, axis=1)[:, None]
                data = data.copy()
                data[bad, :3] = tangent
        return encode("TEXCOORD_0", data, stride, settings)
    meshopt.MeshoptEncoder.encode_attribute = staticmethod(encode_exact)
    try:
        bpy.ops.export_scene.gltf(
            filepath=path,
            export_format="GLB",
            use_selection=True,
            export_apply=True,
            export_cameras=False,
            export_lights=False,
            export_yup=True,
            export_tangents=True,
            export_meshopt_compression_enable=True,
            export_meshopt_extension="EXT_meshopt_compression",
        )
    finally:
        meshopt.MeshoptEncoder.encode_attribute = staticmethod(encode)
    print(f"[tile_kit] exported {path}")


def setup_iso_render(target=(0, 0, .75), span=18.5, sun_energy=2.5, bg=(0.78, 0.86, 0.98)):
    """Orthographic three-quarter camera matching the framing the site uses."""
    cam_data = bpy.data.cameras.new("IsoCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = max(span, 18.5)
    cam = bpy.data.objects.new("IsoCam", cam_data)
    bpy.context.collection.objects.link(cam)

    dist = 30.0
    cam.location = (target[0] + dist * 0.5774, target[1] - dist * 0.5774, target[2] + dist * 0.5774)
    cam.rotation_euler = (math.radians(54.736), 0, math.radians(45))
    bpy.context.scene.camera = cam

    sun_data = bpy.data.lights.new("Sun", type="SUN")
    sun_data.energy = sun_energy
    sun_data.angle = math.radians(8)
    sun_data.color = (1, .88, .72)
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
        bgn.inputs["Strength"].default_value = 0.45
    fill_data = bpy.data.lights.new("Sky bounce", "AREA")
    fill_data.energy = 650
    fill_data.shape = "DISK"
    fill_data.size = 10
    fill_data.color = (.70, .83, 1)
    fill = bpy.data.objects.new("Sky bounce", fill_data)
    bpy.context.collection.objects.link(fill)
    fill.location = (-6, 1, 9)
    fill.rotation_euler = (Vector(target) - fill.location).to_track_quat("-Z", "Y").to_euler()
    return cam


def render_preview(path, resolution=1100, samples=32, transparent=False):
    """`transparent=True` renders the poster used as the card's fallback image
    before the .glb loads (and on devices where WebGL is unavailable), so it has
    to sit on whatever card background the site uses."""
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 6
    try:
        scene.cycles.device = "CPU"
    except Exception:
        pass
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    original_span = scene.camera.data.ortho_scale
    original_location = scene.camera.location.copy()
    if transparent:
        scene.render.resolution_x = round(resolution * 1.65)
        # Fit actual projected vertices, including the slab's lower corner,
        # rather than guessing a square camera's crop for a landscape poster.
        bpy.context.view_layer.update()
        view = scene.camera.matrix_world.inverted()
        projected = [view @ obj.matrix_world @ vertex.co
                     for obj in scene.objects if obj.type == "MESH" and obj.name.endswith("_tile")
                     for vertex in obj.data.vertices]
        left, right = min(v.x for v in projected), max(v.x for v in projected)
        bottom, top = min(v.y for v in projected), max(v.y for v in projected)
        aspect = scene.render.resolution_x / scene.render.resolution_y
        scene.camera.data.ortho_scale = max(right - left, (top - bottom) * aspect) * 1.14
        scene.camera.location += scene.camera.rotation_euler.to_matrix() @ Vector(((left + right) / 2, (bottom + top) / 2, 0))
    scene.render.film_transparent = transparent
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    scene.render.filepath = path

    # Filmic highlight rolloff keeps pale marble and metallic finials readable.
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0

    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    scene.camera.data.ortho_scale = original_span
    scene.camera.location = original_location
    if transparent:
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        slug = os.path.splitext(os.path.basename(path))[0]
        save_source(os.path.join(root, "blender-output", "scenes", slug + ".blend"))
    print(f"[tile_kit] rendered {path}")

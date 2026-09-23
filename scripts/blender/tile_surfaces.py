"""Deterministic, seamless PBR textures embedded in the browser's GLB files.

Images, rather than Blender-only shader noise, keep the same surface detail in
Cycles and Three.js. The normal and roughness maps are shared by material family.
"""
import math
import os
import zlib

import bpy
import numpy as np

SIZE = 256
_fields = {}


def family(name):
    for key, words in (
        ("water", ("water",)),
        ("granite", ("granite",)),
        ("marble", ("marble", "white", "cream")),
        ("ground", ("ground", "earth", "sand", "mud")),
        ("asphalt", ("asphalt", "rubber")),
        ("leaf", ("leaf", "scrub")),
        ("wood", ("trunk", "boat", "wood")),
        ("thatch", ("thatch",)),
        ("plain", ("glass", "gold", "car_", "line", "flag", "cloth", "awning", "spot", "leopard", "camel", "sheep", "croc", "iron", "light", "shadow")),
    ):
        if any(word in name for word in words):
            return key
    return "stone"


def field(kind):
    if kind in _fields:
        return _fields[kind]
    rng = np.random.default_rng(zlib.crc32(kind.encode()))
    y, x = np.mgrid[0:SIZE, 0:SIZE].astype(np.float32) / SIZE
    noise = np.zeros_like(x)
    # Integer frequencies make both value and derivative continuous at the seam.
    for frequency, weight in ((2, .42), (5, .24), (13, .14), (29, .08), (67, .035)):
        for _ in range(4):
            a, b = rng.integers(-frequency, frequency + 1, 2)
            noise += weight * np.sin(math.tau * (a * x + b * y) + rng.uniform(0, math.tau)) / 4
    grain = rng.normal(0, .035, x.shape)
    height = noise * .35 + grain
    shade = 1 + noise * .32 + grain * .7
    rough = np.clip(.76 + noise * .18, .4, .96)
    if kind == "stone":
        row = np.floor(y * 8)
        u = (x * 5 + (row % 2) * .5) % 1
        v = (y * 8) % 1
        mortar = (u < .027) | (v < .036)
        shade *= np.where(mortar, .72, 1)
        height -= mortar * .14
    elif kind == "granite":
        speckles = rng.random(x.shape)
        shade *= np.where(speckles < .12, .62, np.where(speckles > .86, 1.3, 1))
        seams = np.exp(-np.square(np.sin(math.tau * (x * 2 + y) + noise * 2) / .035))
        shade *= 1 - seams * .18
        height -= seams * .09
    elif kind == "marble":
        veins = np.exp(-np.square(np.sin(math.tau * (x + 2 * y) + noise * 4) / .085))
        shade = .99 + noise * .10 - veins * .10 + grain * .18
        height *= .12
        rough = .43 + noise * .12
    elif kind == "water":
        waves = np.sin(math.tau * (3 * x + 11 * y) + noise * 3) * .10
        waves += np.sin(math.tau * (9 * x + 23 * y)) * .028
        height = waves
        shade = .98 + noise * .18 + waves * .16
        rough = .20 + noise * .055
    elif kind in ("wood", "thatch"):
        grain_lines = np.sin(math.tau * (x * (42 if kind == "thatch" else 16)) + noise * 3)
        shade *= 1 + grain_lines * .12
        height += grain_lines * .06
    elif kind == "asphalt":
        shade = .92 + grain * 2.5 + noise * .12
        rough = .87 + noise * .06
    elif kind == "ground":
        shade = .97 + noise * .40 + grain * .55
        height = noise * .5 + grain * .7
    elif kind == "leaf":
        shade = .94 + noise * .65 + grain
        rough = .82 + noise * .10
    # OpenGL tangent-space normals, using periodic central differences.
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * 2.3
    dy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * 2.3
    normal = np.stack((-dx, -dy, np.ones_like(dx)), axis=-1)
    normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
    _fields[kind] = (np.clip(shade, .42, 1.42), rough, normal * .5 + .5)
    return _fields[kind]


def bitmap(name, rgb, data=False):
    existing = bpy.data.images.get(name)
    if existing:
        return existing
    im = bpy.data.images.new(name, width=SIZE, height=SIZE, alpha=False)
    im.colorspace_settings.name = "Non-Color" if data else "sRGB"
    rgba = np.ones((SIZE, SIZE, 4), dtype=np.float32)
    rgba[:, :, :3] = np.clip(rgb, 0, 1)
    im.pixels.foreach_set(rgba.ravel())
    im.pack()
    return im


def material(name, color, roughness=.7, metallic=0):
    existing = bpy.data.materials.get(name)
    if existing:
        return existing
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (*color, 1)
    kind = family(name)
    m["surface_family"] = kind
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    linear = tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in color)
    bsdf.inputs["Base Color"].default_value = (*linear, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if kind == "plain":
        return m
    shade, rough, normal = field(kind)
    nodes, links = m.node_tree.nodes, m.node_tree.links
    base = nodes.new("ShaderNodeTexImage")
    base.image = bitmap(name + "_albedo", shade[:, :, None] * np.array(color))
    links.new(base.outputs["Color"], bsdf.inputs["Base Color"])
    n = nodes.new("ShaderNodeTexImage")
    n.image = bitmap(kind + "_normal", normal, True)
    nm = nodes.new("ShaderNodeNormalMap")
    nm.inputs["Strength"].default_value = .65 if kind != "water" else .28
    links.new(n.outputs["Color"], nm.inputs["Color"])
    links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    orm = nodes.new("ShaderNodeTexImage")
    orm.image = bitmap(kind + "_roughness", np.stack((np.ones_like(rough), rough, np.zeros_like(rough)), axis=-1), True)
    separate = nodes.new("ShaderNodeSeparateColor")
    links.new(orm.outputs["Color"], separate.inputs["Color"])
    links.new(separate.outputs["Green"], bsdf.inputs["Roughness"])
    return m


def prepare(objects):
    """World-scale box projection: no stretching of stone courses on tall walls."""
    bpy.context.view_layer.update()
    for obj in objects:
        if obj.type != "MESH":
            continue
        mesh = obj.data
        uv = mesh.uv_layers.active or mesh.uv_layers.new(name="UVMap")
        normal_matrix = obj.matrix_world.to_3x3().inverted().transposed()
        for poly in mesh.polygons:
            material = mesh.materials[poly.material_index] if mesh.materials else None
            kind = material.get("surface_family", "plain") if material else "plain"
            scale = {"stone": 1.4, "granite": 1.1, "marble": 1.2, "ground": .65,
                     "water": .45, "wood": 2, "thatch": 2, "leaf": 3, "asphalt": 2}.get(kind, 1)
            normal = normal_matrix @ poly.normal
            axis = max(range(3), key=lambda i: abs(normal[i]))
            for loop in poly.loop_indices:
                v = obj.matrix_world @ mesh.vertices[mesh.loops[loop].vertex_index].co
                coords = (v.y, v.z) if axis == 0 else (v.x, v.z) if axis == 1 else (v.x, v.y)
                uv.data[loop].uv = (coords[0] * scale, coords[1] * scale)


def save_source(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)

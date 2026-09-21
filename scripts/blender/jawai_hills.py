"""
Jawai Bandh — photoreal hero asset: granite kopje boulder hill, reservoir edge,
acacia trees, Rabari huts with colourful trim. See scripts/blender/rajasthan_kit.py
for shared helpers (do not edit that file).

Run:
  /Applications/Blender.app/Contents/MacOS/Blender --background --python jawai_hills.py
"""
import os
import sys
import math
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from rajasthan_kit import (
    clear_scene, cube, cylinder, join, bevel,
    flat_material, smart_uv,
    bake_procedural_to_texture, export_glb,
    setup_preview_camera_and_light, render_preview,
)

random.seed(7)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def bold_granite_material(name):
    """Big, unmistakable ochre/rust-vs-gray patches for the kopje boulders —
    a local (non-shared-kit) material tuned to read clearly at hero-camera
    distance, per the user's 'must be obviously colourful' direction."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    for n in list(nodes):
        nodes.remove(n)

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.8
    bsdf.inputs["Metallic"].default_value = 0.0

    tex_coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")

    noise1 = nodes.new("ShaderNodeTexNoise")
    noise1.inputs["Scale"].default_value = 2.0
    noise1.inputs["Detail"].default_value = 2.5

    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.38
    ramp.color_ramp.elements[0].color = (0.33, 0.32, 0.32, 1)
    ramp.color_ramp.elements[1].position = 0.62
    ramp.color_ramp.elements[1].color = (0.74, 0.30, 0.08, 1)

    links.new(tex_coord.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise1.inputs["Vector"])
    links.new(noise1.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    ramp.name = "BakeColorSource"
    mat["bake_color_node"] = ramp.name
    return mat


def dist(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def midpoint(a, b):
    return tuple((a[i] + b[i]) / 2 for i in range(3))


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def flag_string(name, p0, p1, colors, count=6, size=0.16):
    objs = []
    rope_mat = flat_material(f"{name}_RopeMat", (0.35, 0.3, 0.25), roughness=0.9)
    rope = cylinder(f"{name}_rope", 0.015, dist(p0, p1), midpoint(p0, p1), segments=4, material=rope_mat)
    import mathutils
    direction = tuple(p1[i] - p0[i] for i in range(3))
    rope.rotation_euler = mathutils.Vector(direction).to_track_quat("Z", "Y").to_euler()
    bpy.context.view_layer.objects.active = rope
    rope.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    objs.append(rope)
    for i in range(count):
        t = (i + 0.5) / count
        pos = lerp(p0, p1, t)
        pos = (pos[0], pos[1], pos[2] - size * 0.6)
        col = colors[i % len(colors)]
        mat = flat_material(f"{name}_flag{i}", col, roughness=0.6)
        bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=size, depth=size * 1.1, location=pos, end_fill_type="NGON")
        flag = bpy.context.active_object
        flag.name = f"{name}_flag{i}"
        flag.rotation_euler = (math.radians(90), 0, 0)
        flag.data.materials.append(mat)
        objs.append(flag)
    return objs


def boulder(name, radius, location, scale_irregular, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=9, radius=radius, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale_irregular
    obj.rotation_euler = (random.uniform(0, math.pi), random.uniform(0, math.pi), random.uniform(0, math.pi))
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bevel(obj, width=0.05, segments=2)
    obj.data.materials.append(mat)
    return obj


def acacia_tree(name, location, trunk_h=1.4, canopy_r=0.9):
    trunk_mat = flat_material(f"{name}_trunk", (0.32, 0.22, 0.14), roughness=0.9)
    canopy_mat = flat_material(f"{name}_canopy", (0.24, 0.55, 0.18), roughness=0.75)
    trunk = cylinder(f"{name}_trunk", 0.07, trunk_h, (location[0], location[1], location[2] + trunk_h / 2),
                      segments=6, material=trunk_mat)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6, radius=canopy_r,
                                          location=(location[0], location[1], location[2] + trunk_h + canopy_r * 0.35))
    canopy = bpy.context.active_object
    canopy.name = f"{name}_canopy"
    canopy.scale = (1.3, 1.3, 0.55)
    bpy.context.view_layer.objects.active = canopy
    canopy.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    canopy.data.materials.append(canopy_mat)
    return join([trunk, canopy], name)


def rabari_hut(name, location, trim_color, rotation_z=0.0):
    wall_mat = flat_material(f"{name}_wall", (0.90, 0.87, 0.79), roughness=0.85)
    roof_mat = flat_material(f"{name}_roof", (0.45, 0.32, 0.18), roughness=0.9)
    trim_mat = flat_material(f"{name}_trim", trim_color, roughness=0.5)

    body = cylinder(f"{name}_body", 0.75, 0.85, (location[0], location[1], location[2] + 0.42),
                     segments=14, material=wall_mat)
    trim = cylinder(f"{name}_trim", 0.78, 0.55, (location[0], location[1], location[2] + 0.98),
                     segments=14, material=trim_mat)
    roof = cylinder(f"{name}_roof", 0.86, 0.75, (location[0], location[1], location[2] + 1.62),
                     segments=14, material=roof_mat, cone_ratio=0.05)
    hut = join([body, trim, roof], name)
    hut.rotation_euler = (0, 0, rotation_z)
    bpy.context.view_layer.objects.active = hut
    hut.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    return hut


def build():
    clear_scene()

    granite_mat = bold_granite_material("JawaiGranite")
    sand_mat = flat_material("JawaiSand", (0.66, 0.53, 0.36), roughness=0.9)
    water_mat = flat_material("JawaiWater", (0.05, 0.62, 0.64), roughness=0.08, metallic=0.2)
    dam_mat = flat_material("DamStone", (0.55, 0.52, 0.48), roughness=0.8)

    ground = cube("Ground", (5.2, 5.2, 0.3), (0, 0, -0.15), material=sand_mat)

    water = cube("Water", (3.3, 2.6, 0.05), (3.2, -2.9, 0.02), material=water_mat)

    dam = cube("DamWall", (0.7, 1.7, 0.9), (1.6, -3.6, 0.45), material=dam_mat)
    bevel(dam, width=0.05, segments=1)

    # Boulders clustered mid/back (positive Y) so the foreground (negative Y,
    # nearer the preview camera) stays clear for huts/water/dam/trees.
    boulders = []
    cluster_specs = [
        ((-2.0, 3.4, 0.0), 3.3, (1.15, 0.95, 1.0)),
        ((1.6, 2.1, 0.0), 2.7, (1.0, 1.2, 0.9)),
        ((-4.0, 1.9, 0.0), 2.1, (1.1, 1.0, 1.05)),
        ((3.3, 3.3, 0.0), 1.9, (0.95, 1.05, 1.0)),
        ((-0.5, 5.0, 0.0), 2.0, (1.05, 1.0, 0.95)),
        ((-3.1, 3.5, 0.0), 1.4, (1.0, 1.0, 1.1)),
    ]
    for i, (pos, r, sc) in enumerate(cluster_specs):
        b = boulder(f"Boulder{i}", r, (pos[0], pos[1], r * 0.55), sc, granite_mat)
        boulders.append(b)

    huts = [
        rabari_hut("Hut1", (-3.1, -2.0, 0.0), (0.72, 0.12, 0.10), rotation_z=0.4),
        rabari_hut("Hut2", (1.5, -1.8, 0.0), (0.08, 0.25, 0.62), rotation_z=-0.3),
    ]

    trees = [
        acacia_tree("Acacia1", (-4.3, -0.6, 0.0), trunk_h=1.6, canopy_r=1.0),
        acacia_tree("Acacia2", (4.2, -0.6, 0.0), trunk_h=1.3, canopy_r=0.8),
        acacia_tree("Acacia3", (0.0, -3.4, 0.0), trunk_h=1.1, canopy_r=0.7),
    ]

    flags = flag_string(
        "Bunting",
        (-2.35, -2.2, 1.85), (1.05, -1.95, 1.75),
        colors=[(0.85, 0.15, 0.12), (0.10, 0.40, 0.75), (0.95, 0.72, 0.08), (0.15, 0.55, 0.25)],
        count=7, size=0.24,
    )

    smart_uv(boulders[0])
    bake_procedural_to_texture(boulders[0], granite_mat, size=1536, samples=32)
    for b in boulders[1:]:
        smart_uv(b)

    all_static = [ground, water, dam] + boulders + huts + trees + flags
    scene_obj = join(all_static, "JawaiHills")
    scene_obj.location = (0, 0, 0)

    export_path = os.path.join(PROJECT_ROOT, "public", "models", "jawai_hills.glb")
    export_glb(export_path, objects=[scene_obj])

    setup_preview_camera_and_light((18, -22, 10), target=(0, 0.5, 2.6), light_energy=5.0)
    render_preview(os.path.join(PROJECT_ROOT, "public", "models", "previews", "jawai_hills_hero.png"), samples=64)

    print(f"DONE verts~{len(scene_obj.data.vertices)} polys~{len(scene_obj.data.polygons)}")


build()

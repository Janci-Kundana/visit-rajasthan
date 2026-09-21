"""
Jawai Bandh — isometric diorama: stone slab, boulder clusters, turquoise
reservoir corner, colourful-trim huts, acacia trees, dam-wall suggestion.
See scripts/blender/rajasthan_kit.py for shared helpers (do not edit that file).

Run:
  /Applications/Blender.app/Contents/MacOS/Blender --background --python jawai_iso.py
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

random.seed(11)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def bold_granite_material(name):
    """Same bold ochre/rust-vs-gray patch material as jawai_hills.py, kept
    local (not in the shared kit) — see that file for rationale."""
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


def boulder(name, radius, location, scale_irregular, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=7, radius=radius, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale_irregular
    obj.rotation_euler = (random.uniform(0, math.pi), random.uniform(0, math.pi), random.uniform(0, math.pi))
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.data.materials.append(mat)
    return obj


def acacia_tree(name, location, trunk_h=0.9, canopy_r=0.55):
    trunk_mat = flat_material(f"{name}_trunk", (0.32, 0.22, 0.14), roughness=0.9)
    canopy_mat = flat_material(f"{name}_canopy", (0.26, 0.58, 0.2), roughness=0.75)
    trunk = cylinder(f"{name}_trunk", 0.05, trunk_h, (location[0], location[1], location[2] + trunk_h / 2),
                      segments=6, material=trunk_mat)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=5, radius=canopy_r,
                                          location=(location[0], location[1], location[2] + trunk_h + canopy_r * 0.35))
    canopy = bpy.context.active_object
    canopy.name = f"{name}_canopy"
    canopy.scale = (1.3, 1.3, 0.55)
    bpy.context.view_layer.objects.active = canopy
    canopy.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    canopy.data.materials.append(canopy_mat)
    return join([trunk, canopy], name)


def rabari_hut(name, location, trim_color, rotation_z=0.0, scale=0.62):
    wall_mat = flat_material(f"{name}_wall", (0.90, 0.87, 0.79), roughness=0.85)
    roof_mat = flat_material(f"{name}_roof", (0.45, 0.32, 0.18), roughness=0.9)
    trim_mat = flat_material(f"{name}_trim", trim_color, roughness=0.5)

    body = cylinder(f"{name}_body", 0.7 * scale, 0.8 * scale, (location[0], location[1], location[2] + 0.4 * scale),
                     segments=12, material=wall_mat)
    trim = cylinder(f"{name}_trim", 0.73 * scale, 0.5 * scale, (location[0], location[1], location[2] + 0.95 * scale),
                     segments=12, material=trim_mat)
    roof = cylinder(f"{name}_roof", 0.80 * scale, 0.65 * scale, (location[0], location[1], location[2] + 1.53 * scale),
                     segments=12, material=roof_mat, cone_ratio=0.05)
    hut = join([body, trim, roof], name)
    hut.rotation_euler = (0, 0, rotation_z)
    bpy.context.view_layer.objects.active = hut
    hut.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    return hut


def build():
    clear_scene()

    slab_mat = flat_material("SlabStone", (0.83, 0.78, 0.68), roughness=0.7)
    granite_mat = bold_granite_material("JawaiGraniteIso")
    water_mat = flat_material("JawaiWaterIso", (0.05, 0.62, 0.64), roughness=0.08, metallic=0.2)
    dam_mat = flat_material("DamStoneIso", (0.56, 0.53, 0.49), roughness=0.8)
    road_faint_mat = flat_material("DirtPath", (0.62, 0.53, 0.4), roughness=0.9)

    slab_top = cube("SlabTop", (7.2, 7.2, 0.5), (0, 0, -0.25), material=slab_mat)
    bevel(slab_top, width=0.06, segments=1)
    slab_base = cube("SlabBase", (6.9, 6.9, 0.3), (0, 0, -0.65), material=slab_mat)

    water = cube("WaterIso", (1.7, 1.5, 0.05), (2.6, -2.5, 0.02), material=water_mat)
    dam = cube("DamWallIso", (0.4, 1.4, 0.5), (2.0, -2.8, 0.25), material=dam_mat)

    path = cube("DirtPath", (0.5, 4.5, 0.02), (-3.0, 0.5, 0.01), material=road_faint_mat)

    boulders = []
    specs = [
        ((-1.4, 1.6, 0.0), 1.3, (1.1, 0.9, 1.0)),
        ((0.6, 2.4, 0.0), 0.9, (1.0, 1.1, 0.95)),
        ((-2.6, -1.4, 0.0), 1.0, (1.05, 1.0, 1.0)),
        ((2.0, -0.8, 0.0), 0.7, (0.95, 1.0, 1.05)),
    ]
    for i, (pos, r, sc) in enumerate(specs):
        b = boulder(f"BoulderIso{i}", r, (pos[0], pos[1], r * 0.5), sc, granite_mat)
        boulders.append(b)

    huts = [
        rabari_hut("HutIso1", (2.8, 2.2, 0.0), (0.72, 0.12, 0.10), rotation_z=0.5),
        rabari_hut("HutIso2", (-1.0, -2.6, 0.0), (0.08, 0.25, 0.62), rotation_z=-0.2),
    ]

    trees = [
        acacia_tree("AcaciaIso1", (-3.4, 1.8, 0.0)),
        acacia_tree("AcaciaIso2", (1.4, -2.6, 0.0), trunk_h=0.7, canopy_r=0.45),
        acacia_tree("AcaciaIso3", (3.6, 0.6, 0.0), trunk_h=0.75, canopy_r=0.48),
    ]

    smart_uv(boulders[0])
    bake_procedural_to_texture(boulders[0], granite_mat, size=1024, samples=20)
    for b in boulders[1:]:
        smart_uv(b)

    all_static = [slab_top, slab_base, water, dam, path] + boulders + huts + trees
    scene_obj = join(all_static, "JawaiIso")
    scene_obj.location = (0, 0, 0)

    export_path = os.path.join(PROJECT_ROOT, "public", "models", "jawai_iso.glb")
    export_glb(export_path, objects=[scene_obj])

    setup_preview_camera_and_light((16, -18, 18), target=(0, 0, 0), light_energy=4.0)
    render_preview(os.path.join(PROJECT_ROOT, "public", "models", "previews", "jawai_iso_hero.png"))

    print(f"DONE verts~{len(scene_obj.data.vertices)} polys~{len(scene_obj.data.polygons)}")


build()

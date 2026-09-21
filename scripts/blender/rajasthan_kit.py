"""
Shared procedural-modeling / baking / export helpers for the "Visit Rajasthan"
asset pipeline. Reused across Jaisalmer, Udaipur, Jaipur and Jawai Bandh builds.

Run headlessly, e.g.:
  /Applications/Blender.app/Contents/MacOS/Blender --background --python jaisalmer_fort.py
"""
import bpy
import bmesh
import math
import random
import os

TAU = math.pi * 2


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block_collection in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.cameras, bpy.data.lights):
        for block in list(block_collection):
            if block.users == 0:
                block_collection.remove(block)


def new_object(name, mesh):
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def cube(name, size, location, material=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = new_object(name, mesh)
    obj.scale = size
    obj.location = location
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    return obj


def cylinder(name, radius, depth, location, segments=12, material=None, cone_ratio=None):
    if cone_ratio is not None:
        bpy.ops.mesh.primitive_cone_add(
            vertices=segments,
            radius1=radius,
            radius2=radius * cone_ratio,
            depth=depth,
            location=location,
            end_fill_type="NGON",
        )
    else:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=segments,
            radius=radius,
            depth=depth,
            location=location,
            end_fill_type="NGON",
        )
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj


def dome(name, radius, location, material=None, segments=12, ring_count=6):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments, ring_count=ring_count, radius=radius, location=location
    )
    obj = bpy.context.active_object
    obj.name = name
    # keep only upper hemisphere
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(obj.data)
    to_del = [v for v in bm.verts if v.co.z < -0.02]
    bmesh.ops.delete(bm, geom=to_del, context="VERTS")
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.fill_holes(sides=0)
    bpy.ops.object.mode_set(mode="OBJECT")
    if material:
        obj.data.materials.append(material)
    return obj


def join(objects, name):
    if not objects:
        return None
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    result = bpy.context.active_object
    result.name = name
    return result


def bevel(obj, width=0.03, segments=2):
    m = obj.modifiers.new("Bevel", "BEVEL")
    m.width = width
    m.segments = segments
    m.limit_method = "ANGLE"
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=m.name)


def procedural_sandstone_material(name="Sandstone", base_hex=(0.78, 0.62, 0.36), dark_hex=(0.42, 0.30, 0.18)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    for n in list(nodes):
        nodes.remove(n)

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.75
    bsdf.inputs["Metallic"].default_value = 0.0

    tex_coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")

    noise1 = nodes.new("ShaderNodeTexNoise")
    noise1.inputs["Scale"].default_value = 8.0
    noise1.inputs["Detail"].default_value = 6.0

    voronoi = nodes.new("ShaderNodeTexVoronoi")
    voronoi.inputs["Scale"].default_value = 22.0

    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*dark_hex, 1)
    ramp.color_ramp.elements[1].color = (*base_hex, 1)

    mixrgb = nodes.new("ShaderNodeMixRGB")
    mixrgb.blend_type = "MULTIPLY"
    mixrgb.inputs["Fac"].default_value = 0.25

    links.new(tex_coord.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise1.inputs["Vector"])
    links.new(mapping.outputs["Vector"], voronoi.inputs["Vector"])
    links.new(noise1.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], mixrgb.inputs["Color1"])
    links.new(voronoi.outputs["Distance"], mixrgb.inputs["Color2"])
    links.new(mixrgb.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    mixrgb.name = "BakeColorSource"
    mat["bake_color_node"] = mixrgb.name
    return mat


def flat_material(name, color, roughness=0.85, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def smart_uv(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")


def bake_procedural_to_texture(obj, mat, size=1536, samples=24):
    """Wires the material's procedural color graph into an Emission shader,
    bakes it (with Cycles AO multiplied in) to an image, then rewires the
    Principled BSDF's Base Color to read from that baked image so it survives
    glTF export."""
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    try:
        scene.cycles.device = "CPU"
    except Exception:
        pass

    smart_uv(obj)

    img_name = f"{mat.name}_baked"
    img = bpy.data.images.new(img_name, width=size, height=size)

    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links

    tex_node = nodes.new("ShaderNodeTexImage")
    tex_node.image = img
    tex_node.select = True
    nt.nodes.active = tex_node

    emit = nodes.new("ShaderNodeEmission")
    out = next(n for n in nodes if n.type == "OUTPUT_MATERIAL")

    color_src = None
    node_name = mat.get("bake_color_node")
    if node_name and node_name in nodes:
        src_node = nodes[node_name]
        if "Color" in src_node.outputs:
            color_src = src_node.outputs["Color"]

    if color_src is not None:
        links.new(color_src, emit.inputs["Color"])
    else:
        print(f"WARNING: no bake_color_node found for material {mat.name}; baking flat white")
    old_link = out.inputs["Surface"].links[0] if out.inputs["Surface"].links else None
    if old_link:
        links.remove(old_link)
    links.new(emit.outputs["Emission"], out.inputs["Surface"])

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.bake(type="EMIT")

    img.filepath_raw = f"//baked_{img_name}.png"
    img.file_format = "PNG"

    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    nodes.remove(emit)

    return img


def export_glb(path, objects=None):
    bpy.ops.object.select_all(action="DESELECT")
    if objects:
        for o in objects:
            o.select_set(True)
        use_selection = True
    else:
        use_selection = False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        use_selection=use_selection,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
        export_yup=True,
    )


def setup_preview_camera_and_light(cam_loc, target=(0, 0, 0), light_energy=4.0):
    cam_data = bpy.data.cameras.new("PreviewCam")
    cam_data.lens = 38
    cam_obj = bpy.data.objects.new("PreviewCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = cam_loc
    direction = (
        target[0] - cam_loc[0],
        target[1] - cam_loc[1],
        target[2] - cam_loc[2],
    )
    import mathutils

    cam_obj.rotation_euler = mathutils.Vector(direction).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam_obj

    sun_data = bpy.data.lights.new("Sun", type="SUN")
    sun_data.energy = light_energy
    sun_data.angle = math.radians(2.5)
    sun_obj = bpy.data.objects.new("Sun", sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.location = (10, -10, 20)
    sun_obj.rotation_euler = (math.radians(55), 0, math.radians(35))

    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.85, 0.78, 0.68, 1)
        bg.inputs["Strength"].default_value = 0.9

    return cam_obj


def render_preview(path, resolution=900, samples=48):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True)

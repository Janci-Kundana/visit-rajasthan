"""
Jawai Bandh — leopard hills and dam.

The odd one out: Jawai has no monument. Its identity is landform and wildlife, so
this tile is built from terrain rather than architecture.

Landmarks:
  * Granite koppies — the smooth, rounded boulder hills leopards den in. These are
    the silhouette; everything else is supporting cast.
  * Jawai Bandh     — the dam wall and its reservoir, which is the place's name.
  * A leopard on a rock, and crocodiles in the shallows.
  * Rabari settlement — round thatched huts and a herd, the human half of the deal.

Build:
  /Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/blender/jawai_tile.py
"""
import bpy
import math
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import tile_kit as K
import tile_details as D

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT_GLB = os.path.join(ROOT, "public", "models", "jawai_tile.glb")
OUT_PNG = os.path.join(ROOT, "blender-output", "tiles", "jawai_tile.png")
# Transparent poster shown in the card until the .glb finishes loading.
OUT_POSTER = os.path.join(ROOT, "public", "images", "tiles", "jawai.png")

GRANITE = GRANITE_DK = GRANITE_LT = SCRUB = SCRUB_DK = GROUND = EARTH = None
WATER = CONCRETE = ASPHALT = LINE = TRUNK = THATCH = MUD = LEOPARD = SPOT = None
CROC = SHEEP = CLOTH = GLASSY = CAR_A = None


def palette():
    global GRANITE, GRANITE_DK, GRANITE_LT, SCRUB, SCRUB_DK, GROUND, EARTH
    global WATER, CONCRETE, ASPHALT, LINE, TRUNK, THATCH, MUD, LEOPARD, SPOT
    global CROC, SHEEP, CLOTH, GLASSY, CAR_A
    # Jawai is grey granite over dry ochre scrub — a cooler, earthier palette than
    # the other three tiles, which is the point: it should not look like a city.
    GRANITE    = K.mat("jw_granite",    (0.451, 0.435, 0.427))
    GRANITE_DK = K.mat("jw_granite_dk", (0.322, 0.310, 0.310))
    GRANITE_LT = K.mat("jw_granite_lt", (0.561, 0.545, 0.529))
    SCRUB      = K.mat("jw_scrub",      (0.451, 0.510, 0.298))
    SCRUB_DK   = K.mat("jw_scrub_dk",   (0.322, 0.396, 0.220))
    GROUND     = K.mat("jw_ground",     (0.757, 0.686, 0.494))
    EARTH      = K.mat("jw_earth",      (0.600, 0.510, 0.345))
    WATER      = K.mat("jw_water",      (0.180, 0.435, 0.529), roughness=0.16)
    CONCRETE   = K.mat("jw_concrete",   (0.686, 0.675, 0.651))
    ASPHALT    = K.mat("jw_asphalt",    (0.286, 0.278, 0.267))
    LINE       = K.mat("jw_line",       (0.933, 0.925, 0.886))
    TRUNK      = K.mat("jw_trunk",      (0.408, 0.310, 0.208))
    THATCH     = K.mat("jw_thatch",     (0.729, 0.580, 0.310))
    MUD        = K.mat("jw_mud",        (0.796, 0.702, 0.541))
    LEOPARD    = K.mat("jw_leopard",    (0.867, 0.690, 0.365))
    SPOT       = K.mat("jw_spot",       (0.278, 0.224, 0.169))
    CROC       = K.mat("jw_croc",       (0.357, 0.400, 0.290))
    SHEEP      = K.mat("jw_sheep",      (0.886, 0.867, 0.827))
    CLOTH      = K.mat("jw_cloth",      (0.812, 0.267, 0.243))
    GLASSY     = K.glass("jw_glass",    (0.302, 0.510, 0.580))
    CAR_A      = K.mat("jw_car_a",      (0.886, 0.878, 0.859))


def koppie(name, origin, scale=1.0, seed=0):
    """A granite koppie: a pile of weathered boulders, biggest at the bottom.

    Stacking a few irregular ico-spheres reads as Jawai's rock far better than any
    single mesh would — the gaps and overhangs are the whole character.
    """
    ox, oy = origin
    parts = []
    stack = [(0.0, 0.0, 0.0, 1.0), (0.32, 0.18, 0.62, 0.72), (-0.3, -0.22, 0.52, 0.64),
             (0.05, -0.34, 1.05, 0.5), (-0.12, 0.3, 1.12, 0.42)]
    for i, (dx, dy, dz, r) in enumerate(stack):
        parts.append(K.rock(f"{name}_b{i}",
                            (ox + dx * scale, oy + dy * scale, dz * scale + r * scale * 0.42),
                            r * scale,
                            GRANITE if i % 2 == 0 else GRANITE_LT,
                            seed=seed * 17 + i))
    # a couple of dark boulders wedged at the foot
    for i, (dx, dy, r) in enumerate(((0.85, -0.5, 0.3), (-0.8, 0.55, 0.26))):
        parts.append(K.rock(f"{name}_f{i}",
                            (ox + dx * scale, oy + dy * scale, r * scale * 0.4),
                            r * scale, GRANITE_DK, seed=seed * 31 + i))
    return parts


def dam(y=3.3):
    """The bandh itself: a concrete wall holding back the reservoir, with sluice
    piers. It gives the tile a hard man-made line against all the organic rock."""
    parts = []
    parts.append(K.box("dam_wall", (0.0, y, 0.44), (11.4, 0.7, 0.88), CONCRETE))
    parts.append(K.box("dam_cap", (0.0, y, 0.9), (11.6, 0.86, 0.1), GRANITE_LT))
    for i in range(7):
        x = -4.5 + i * 1.5
        parts.append(K.box(f"dam_pier{i}", (x, y - 0.42, 0.62), (0.22, 0.26, 1.24), GRANITE_LT))
        parts.append(K.box(f"dam_gate{i}", (x + 0.75, y - 0.38, 0.34), (0.9, 0.12, 0.68), GRANITE_DK))
    # spillway apron on the dry side
    parts.append(K.box("dam_apron", (0.0, y - 0.95, 0.06), (11.0, 1.2, 0.12), CONCRETE))
    return parts


def reservoir(center=(0.0, 4.7), dims=(11.2, 2.35)):
    return K.water_patch("jawai_water", center, dims, WATER, EARTH, bank=0.1)


def crocodiles():
    parts = []
    for i, (x, y, a) in enumerate(((-3.4, 4.3, 0.4), (2.6, 4.5, -0.6))):
        def p(dx, dy, z):
            return (x + math.cos(a) * dx - math.sin(a) * dy, y + math.sin(a) * dx + math.cos(a) * dy, z)
        parts.append(K.ellipsoid(f"cr{i}_body", p(0, 0, .10), (.31, .095, .055), CROC, a, 3))
        parts.append(K.ellipsoid(f"cr{i}_head", p(.34, 0, .11), (.15, .070, .042), CROC, a))
        parts.append(K.tube(f"cr{i}_tail", [p(-.25, 0, .10), p(-.43, -.03, .09), p(-.62, -.09, .078)], .03, CROC))
        for dx in (-.17, .18):
            for dy in (-.13, .13):
                parts.append(K.ellipsoid(f"cr{i}_leg", p(dx, dy, .084), (.07, .055, .023), CROC, a))
        for j in range(8):
            parts.append(K.cone(f"cr{i}_scute", p(-.22 + j * .065, 0, .157), .023, 0, .037, GRANITE_DK, 4))
    return parts


def rabari_camp(origin=(3.4, -3.4)):
    """Round mud-and-thatch huts with a dry-stone stock pen and a small herd."""
    ox, oy = origin
    parts = []
    for i, (dx, dy, r) in enumerate(((0.0, 0.0, 0.52), (1.15, 0.35, 0.44), (0.5, 1.2, 0.4))):
        parts.append(K.cyl(f"hut{i}_wall", (ox + dx, oy + dy, 0.21), r, 0.42, MUD, verts=14))
        parts.append(K.cone(f"hut{i}_roof", (ox + dx, oy + dy, 0.42 + r * 0.32),
                            r * 1.2, 0.02, r * 0.64, THATCH, verts=14))
        parts.append(K.box(f"hut{i}_door", (ox + dx, oy + dy - r * 0.98, 0.14),
                           (0.16, 0.1, 0.28), SPOT))
        for j in range(28):
            a = K.TAU * j / 28
            parts.append(K.rod("thatch_reed", (ox + dx + math.cos(a) * r * 1.19, oy + dy + math.sin(a) * r * 1.19, .42),
                               (ox + dx + math.cos(a) * .023, oy + dy + math.sin(a) * .023, .42 + r * .64), .009, THATCH, 4))
    # stock pen: a ring of low stones
    for i in range(14):
        a = K.TAU * i / 14.0
        parts.append(K.box(f"pen{i}", (ox - 1.5 + math.cos(a) * 1.05, oy - 1.2 + math.sin(a) * 0.8,
                                       0.09), (0.2, 0.16, 0.18), GRANITE_DK, rot_z=a))
    for i, (dx, dy) in enumerate(((-1.7, -1.3), (-1.35, -1.05), (-1.6, -0.85), (-1.2, -1.4))):
        parts.append(K.ellipsoid(f"sheep{i}_body", (ox + dx, oy + dy, 0.17), (.15, .085, .095), SHEEP))
        parts.append(K.ellipsoid(f"sheep{i}_head", (ox + dx + 0.16, oy + dy, 0.20),
                           (.066, .041, .050), SPOT))
        for lx in (-.08, .08):
            for ly in (-.052, .052):
                parts.append(K.cyl(f"sheep{i}_leg", (ox + dx + lx, oy + dy + ly, .055), .014, .11, SPOT, 6))
    # a herder in a red turban
    parts.append(K.cyl("herder_body", (ox - 0.55, oy - 1.9, 0.19), 0.09, 0.38, CLOTH, verts=8))
    parts.append(K.dome("herder_head", (ox - 0.55, oy - 1.9, 0.38), 0.09, CLOTH))
    return parts


def scrub_trees():
    """Thorn scrub and the odd big banyan — dry-country planting, sparse on purpose."""
    parts = []
    spots = [(-5.2, 0.4, 1.1), (-4.0, -1.5, 0.9), (-2.2, -4.6, 1.0), (0.4, -5.2, 0.85),
             (-5.4, -3.6, 0.95), (5.4, 0.9, 1.0), (5.6, -5.2, 0.9), (1.6, 1.2, 0.8),
             (-1.0, 1.6, 0.75), (3.0, 1.4, 0.85), (-3.4, 1.5, 0.8), (5.5, 2.1, 0.75)]
    for i, (x, y, s) in enumerate(spots):
        parts += K.tree(f"tree{i}", (x, y), s, TRUNK,
                        SCRUB if i % 2 else SCRUB_DK,
                        "round" if i % 4 == 0 else "scrub")
    return parts


def track():
    """A single dirt road. Jawai does not have traffic, and pretending otherwise
    would make it read like the city tiles."""
    parts = []
    dirt = K.mat("jw_track_earth", (.49, .40, .28), .95)
    parts += K.road("trk", (-6, -1.9), (6, -1.9), .95, dirt, None, dashed=False)
    for yy in (-2.10, -1.70):
        parts.append(K.box("wheel_rut", (0, yy, .032), (12, .065, .015), EARTH))
    parts += K.car("jeep", (-1.4, -1.65), 0.0, CAR_A, GLASSY)
    return parts


def build():
    K.clear_scene()
    palette()
    parts = []
    parts += K.base_slab(GROUND, EARTH)
    parts += reservoir()
    parts += dam()
    parts += track()

    # The koppie cluster: one hero, two supporting, scattered off-axis so the
    # composition does not read as a grid like the city tiles do.
    parts += koppie("kop_main", (-2.6, 0.4), scale=1.45, seed=1)
    parts += koppie("kop_two", (1.9, -0.6), scale=0.95, seed=2)
    parts += koppie("kop_three", (-4.6, -3.2), scale=0.8, seed=3)
    parts += koppie("kop_four", (4.6, 1.6), scale=0.62, seed=4)

    # A low, flat-topped lookout boulder: the leopard has to be silhouetted
    # against open ground or it vanishes into the koppie at thumbnail size.
    parts.append(K.rock("lookout", (-0.5, -3.7, 0.34), 0.95, GRANITE, seed=9, squash=0.42))
    parts.append(K.rock("lookout_b", (0.35, -4.2, 0.2), 0.5, GRANITE_DK, seed=11))
    parts += D.leopard("leopard", (-0.55, -3.7, 0.73), .42, LEOPARD, SPOT)
    parts += crocodiles()
    parts += rabari_camp()
    parts += scrub_trees()

    parts += D.railing("dam_guard", (-5.65, 3.0), (5.65, 3.0), .95, GRANITE_DK, .18)
    parts += D.railing("dam_guard_back", (-5.65, 3.6), (5.65, 3.6), .95, GRANITE_DK, .18)
    # Dry grass, gravel and weathered rock fragments occupy open ground only.
    rng = __import__("random").Random(2026)
    dry = K.mat("jw_dry_scrub", (.49, .45, .26), .95)
    for i in range(110):
        x, y = rng.uniform(-5.7, 5.7), rng.uniform(-5.7, 2.2)
        if -2.5 < y < -1.25 or (x > 1.3 and y < -2.2):
            continue
        if i % 3 == 0:
            parts.append(K.ellipsoid("gravel", (x, y, .045), (.09, .07, .055), GRANITE_DK, rng.random() * 6))
        else:
            for j in range(3):
                parts.append(K.rod("dry_grass", (x, y, .015), (x + rng.uniform(-.06, .06), y + rng.uniform(-.06, .06), rng.uniform(.08, .17)), .006, dry, 4))

    tile = K.join_all(parts, "jawai_tile")
    K.export_glb(OUT_GLB, tile)
    K.setup_iso_render(span=15.0)
    K.render_preview(OUT_PNG)
    K.render_preview(OUT_POSTER, resolution=720, transparent=True)


if __name__ == "__main__":
    build()

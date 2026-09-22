"""
Jaipur — the Pink City.

Landmarks chosen because they are unmistakably Jaipur and nowhere else in India:
  * Hawa Mahal      — the five-storey honeycomb facade, the city's shorthand.
  * Chandra Mahal   — the tiered City Palace block behind it.
  * Jantar Mantar   — the Samrat Yantra's giant ramped gnomon, unique on earth.
  * Albert Hall     — the domed Indo-Saracenic museum, anchoring the near corner.

Build:
  /Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/blender/jaipur_tile.py
"""
import bpy
import math
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import tile_kit as K

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT_GLB = os.path.join(ROOT, "public", "models", "jaipur_tile.glb")
OUT_PNG = os.path.join(ROOT, "blender-output", "tiles", "jaipur_tile.png")
# Transparent poster shown in the card until the .glb finishes loading.
OUT_POSTER = os.path.join(ROOT, "public", "images", "tiles", "jaipur.png")

# Jaipur's palette: the old city is painted a terracotta rose with white outlines.
# Built after clear_scene(), which purges unused material datablocks.
PINK = PINK_DEEP = WHITE = GOLD = GROUND = EARTH = ASPHALT = LINE = None
LEAF = LEAF_DARK = TRUNK = GLASSY = CAR_A = CAR_B = CAR_C = None


def palette():
    global PINK, PINK_DEEP, WHITE, GOLD, GROUND, EARTH, ASPHALT, LINE
    global LEAF, LEAF_DARK, TRUNK, GLASSY, CAR_A, CAR_B, CAR_C
    PINK       = K.mat("jp_pink",      (0.855, 0.388, 0.290))
    PINK_DEEP  = K.mat("jp_pink_deep", (0.667, 0.255, 0.188))
    WHITE      = K.mat("jp_white",     (0.962, 0.941, 0.900))
    GOLD       = K.mat("jp_gold",      (0.918, 0.706, 0.278), roughness=0.34, metallic=0.55)
    GROUND     = K.mat("jp_ground",    (0.796, 0.737, 0.620))
    EARTH      = K.mat("jp_earth",     (0.729, 0.639, 0.510))
    ASPHALT    = K.mat("jp_asphalt",   (0.278, 0.290, 0.318))
    LINE       = K.mat("jp_line",      (0.949, 0.949, 0.933))
    LEAF       = K.mat("jp_leaf",      (0.322, 0.596, 0.318))
    LEAF_DARK  = K.mat("jp_leaf_dark", (0.220, 0.470, 0.259))
    TRUNK      = K.mat("jp_trunk",     (0.400, 0.290, 0.204))
    GLASSY     = K.glass("jp_glass",   (0.310, 0.600, 0.690))
    CAR_A      = K.mat("jp_car_a",     (0.910, 0.906, 0.898))
    CAR_B      = K.mat("jp_car_b",     (0.847, 0.271, 0.239))
    CAR_C      = K.mat("jp_car_c",     (0.239, 0.400, 0.710))


def hawa_mahal(origin=(-3.1, 1.6)):
    """Five receding storeys of jharokha windows capped with small domes.

    The real building is famously only one room deep — a screen, not a block — so
    the depth is kept tight and the taper exaggerated. That pyramidal outline of
    tiny windows is the entire recognisability budget at thumbnail size.
    """
    ox, oy = origin
    parts = []
    W0, D = 3.5, 1.05

    parts.append(K.slab_on_ground("hm_plinth", (ox, oy), (W0 + 0.4, D + 0.5), 0.2, PINK_DEEP))

    tier_h = [0.62, 0.56, 0.5, 0.44, 0.38]
    z = 0.2
    for i, h in enumerate(tier_h):
        w = W0 * (1.0 - i * 0.145)
        d = D * (1.0 - i * 0.1)
        oy_i = oy + i * 0.05          # each storey steps back from the street
        parts.append(K.slab_on_ground(f"hm_t{i}", (ox, oy_i), (w, d), h, PINK, z0=z))
        # white string course capping every storey
        parts.append(K.slab_on_ground(f"hm_band{i}", (ox, oy_i), (w + 0.09, d + 0.09), 0.06,
                                      WHITE, z0=z + h))
        # the honeycomb: a band of arched windows per storey, on the street face
        cols = max(3, 9 - i)
        parts += K.window_grid(f"hm_win{i}",
                               (ox, oy_i - d / 2.0, z + h * 0.5),
                               (0, -1), w * 0.95, h * 0.62, 1, cols, WHITE,
                               inset=0.03, pad=0.08)
        z += h + 0.06

    # crown of little domes along the ridge
    for i in range(4):
        x = ox - 0.99 + i * 0.66
        parts += K.onion_dome(f"hm_dome{i}", (x, oy + 0.24, z), 0.15, PINK, GOLD, height_scale=1.3)
    parts += K.chhatri("hm_chhatri_l", (ox - 1.55, oy + 0.24, z - 0.1), 0.3, 0.2, WHITE, PINK)
    parts += K.chhatri("hm_chhatri_r", (ox + 1.55, oy + 0.24, z - 0.1), 0.3, 0.2, WHITE, PINK)
    return parts


def chandra_mahal(origin=(2.6, 3.4)):
    """City Palace's seven-storey block, stepped like a wedding cake."""
    ox, oy = origin
    parts = []
    parts.append(K.slab_on_ground("cm_base", (ox, oy), (3.4, 2.6), 0.9, WHITE))
    parts += K.window_grid("cm_w0", (ox, oy - 1.3, 0.48), (0, -1), 3.2, 0.62, 1, 7, PINK,
                           inset=0.035, pad=0.12)
    parts.append(K.slab_on_ground("cm_t1", (ox, oy), (2.6, 2.0), 0.72, PINK, z0=0.9))
    parts += K.window_grid("cm_w1", (ox, oy - 1.0, 1.26), (0, -1), 2.4, 0.5, 1, 5, WHITE,
                           inset=0.035, pad=0.1)
    parts.append(K.slab_on_ground("cm_t2", (ox, oy), (1.8, 1.45), 0.62, WHITE, z0=1.62))
    parts.append(K.slab_on_ground("cm_t3", (ox, oy), (1.15, 1.0), 0.52, PINK, z0=2.24))

    parts += K.onion_dome("cm_dome", (ox, oy, 2.76), 0.44, GOLD, GOLD, height_scale=1.4)
    for sx, sy in ((-1.5, -1.1), (1.5, -1.1), (-1.5, 1.1), (1.5, 1.1)):
        parts += K.chhatri(f"cm_ch_{sx}_{sy}", (ox + sx, oy + sy, 0.9), 0.42, 0.28, WHITE, PINK)
    return parts


def jantar_mantar(origin=(2.9, -0.4)):
    """Samrat Yantra: a 27m right-triangle gnomon flanked by two quadrant arcs.
    Nothing else in the country looks like it, so it earns its footprint."""
    ox, oy = origin
    parts = []
    parts.append(K.slab_on_ground("jm_court", (ox, oy), (3.0, 2.6), 0.1, EARTH))

    # The gnomon: a right triangle in profile, made by collapsing a box's top
    # face down to the hypotenuse. The steep stair edge is the recognisable bit.
    ramp = K.box("jm_gnomon", (ox - 0.15, oy, 0.85), (2.0, 0.3, 1.5), WHITE)
    for v in ramp.data.vertices:
        if v.co.z > 0:
            v.co.z = -0.75 + (v.co.x + 1.0) * 1.5 / 2.0
    parts.append(ramp)
    parts.append(K.box("jm_gnomon_edge", (ox - 0.15, oy, 0.86), (2.04, 0.12, 1.5), PINK))
    for v in parts[-1].data.vertices:
        if v.co.z > 0:
            v.co.z = -0.75 + (v.co.x + 1.02) * 1.5 / 2.04

    # The quadrant: a curved dial wall sweeping off the gnomon's high end.
    for i in range(9):
        a = math.radians(8 + i * 19)
        h = 0.2 + math.sin(a) * 0.34
        parts.append(K.box(f"jm_quad{i}",
                           (ox + 0.95 + math.cos(a) * 0.55,
                            oy - 0.15 + math.sin(a) * 0.95,
                            0.1 + h / 2.0),
                           (0.2, 0.2, h), PINK_DEEP, rot_z=a))
    # Jai Prakash Yantra: the sunken hemispherical bowl dial.
    parts.append(K.cyl("jm_bowl_rim", (ox - 1.15, oy - 0.85, 0.16), 0.42, 0.12, WHITE, verts=18))
    parts.append(K.cyl("jm_bowl", (ox - 1.15, oy - 0.85, 0.24), 0.31, 0.06, PINK_DEEP, verts=18))
    return parts


def albert_hall(origin=(-3.2, -3.0)):
    """Indo-Saracenic museum: long arcaded body, big central dome, corner spires."""
    ox, oy = origin
    parts = []
    parts.append(K.slab_on_ground("ah_body", (ox, oy), (3.2, 1.7), 0.72, WHITE))
    parts += K.window_grid("ah_arch", (ox, oy - 0.85, 0.38), (0, -1), 3.0, 0.5, 1, 7, PINK,
                           inset=0.035, pad=0.1)
    parts.append(K.slab_on_ground("ah_upper", (ox, oy), (1.5, 1.4), 0.5, PINK, z0=0.72))
    parts += K.onion_dome("ah_dome", (ox, oy, 1.22), 0.52, PINK_DEEP, GOLD, height_scale=1.3)
    for sx in (-1.35, 1.35):
        parts += K.chhatri(f"ah_ch{sx}", (ox + sx, oy, 0.72), 0.34, 0.24, WHITE, PINK_DEEP)
    return parts


def old_city_block(origin=(-2.4, -4.3)):
    """Generic pink-plastered haveli terrace. Jaipur's old city is a continuous
    painted street wall, so the filler blocks matter as much as the monuments."""
    parts = []
    ox, oy = origin
    for i, (dx, w, d, h) in enumerate(((-1.5, 1.2, 1.4, 0.95),
                                       (-0.2, 1.3, 1.6, 1.25),
                                       (1.2, 1.4, 1.35, 0.8))):
        body = PINK if i % 2 == 0 else PINK_DEEP
        parts.append(K.slab_on_ground(f"blk{i}", (ox + dx, oy), (w, d), h, body))
        parts.append(K.slab_on_ground(f"blk{i}_cap", (ox + dx, oy), (w + 0.12, d + 0.12),
                                      0.08, WHITE, z0=h))
        parts += K.window_grid(f"blk{i}_w", (ox + dx, oy - d / 2.0, h * 0.55),
                               (0, -1), w * 0.9, h * 0.5, 1, 3, WHITE, inset=0.03, pad=0.08)
        parts += K.crenellation(f"blk{i}_cr", (ox + dx - w / 2, oy - d / 2),
                                (ox + dx + w / 2, oy - d / 2), h + 0.08, WHITE,
                                merlon=0.1, gap=0.14, height=0.14)
    return parts


JUNCTION = (0.55, -1.85)


def streets():
    parts = []
    skip = [(JUNCTION[0], JUNCTION[1], 1.15)]
    # Vertical road sits on the lower layer, horizontal crosses over it.
    parts += K.road("rd_v", (0.55, -6), (0.55, 6), 1.35, ASPHALT, LINE, layer=0, skip=skip)
    parts += K.road("rd_h", (-6, -1.85), (6, -1.85), 1.5, ASPHALT, LINE, layer=1, skip=skip)
    # Kerbs only on the outer runs, so they don't cut across the junction.
    parts += K.kerb("kb_h_l", (-6, -1.85), (-0.5, -1.85), 1.5, GROUND)
    parts += K.kerb("kb_h_r", (1.6, -1.85), (6, -1.85), 1.5, GROUND)
    parts += K.kerb("kb_v_b", (0.55, -6), (0.55, -2.9), 1.35, GROUND)
    parts += K.kerb("kb_v_t", (0.55, -0.8), (0.55, 6), 1.35, GROUND)

    for i, (pos, ang, m) in enumerate((
        ((-3.4, -1.55), 0.0, CAR_A), ((-1.4, -2.15), math.pi, CAR_B),
        ((2.9, -1.55), 0.0, CAR_C), ((4.8, -2.15), math.pi, CAR_A),
        ((0.25, 2.4), math.pi / 2, CAR_B), ((0.85, -4.2), -math.pi / 2, CAR_C),
        ((0.25, 4.7), math.pi / 2, CAR_A), ((-5.2, -1.55), 0.0, CAR_C),
        ((0.85, 0.6), -math.pi / 2, CAR_A),
    )):
        parts += K.car(f"car{i}", pos, ang, m, GLASSY)
    return parts


def greenery():
    parts = []
    spots = [(-5.3, -0.8, 1.0), (-4.2, -0.8, 0.85), (-0.7, -0.8, 0.9), (2.0, -0.85, 0.95),
             (4.4, -0.8, 0.85), (5.3, 1.4, 1.0), (-5.4, 3.2, 0.95), (-5.2, 5.0, 0.8),
             (-1.4, 4.9, 0.9), (5.2, -3.6, 0.95), (2.0, -4.6, 0.85), (-1.5, -4.4, 1.0),
             (-4.6, -5.0, 0.9), (4.6, 4.9, 0.9), (-2.6, -0.85, 0.8)]
    for i, (x, y, s) in enumerate(spots):
        kind = "palm" if i % 5 == 0 else "round"
        parts += K.tree(f"tree{i}", (x, y), s, TRUNK, LEAF if i % 2 else LEAF_DARK, kind)
    return parts


def build():
    K.clear_scene()
    palette()
    parts = []
    parts += K.base_slab(GROUND, EARTH)
    parts += streets()
    parts += hawa_mahal()
    parts += chandra_mahal()
    parts += jantar_mantar()
    parts += albert_hall()
    parts += old_city_block()
    parts += greenery()

    tile = K.join_all(parts, "jaipur_tile")
    K.export_glb(OUT_GLB, tile)

    K.setup_iso_render(span=15.0)
    K.render_preview(OUT_PNG)
    K.render_preview(OUT_POSTER, resolution=720, transparent=True)


if __name__ == "__main__":
    build()

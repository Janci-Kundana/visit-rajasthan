"""
Udaipur — the City of Lakes.

Landmarks:
  * Taj Lake Palace — white marble palace filling its own island on Lake Pichola.
    A palace that appears to float is the single image people hold of Udaipur.
  * City Palace     — the long shoreline facade with octagonal towers and cupolas,
    the largest palace complex in Rajasthan.
  * Jag Mandir      — the smaller domed island pavilion further out.
  * Lake Pichola    — takes nearly half the tile, because the water IS the city.

Build:
  /Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/blender/udaipur_tile.py
"""
import bpy
import math
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import tile_kit as K

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT_GLB = os.path.join(ROOT, "public", "models", "udaipur_tile.glb")
OUT_PNG = os.path.join(ROOT, "blender-output", "tiles", "udaipur_tile.png")
# Transparent poster shown in the card until the .glb finishes loading.
OUT_POSTER = os.path.join(ROOT, "public", "images", "tiles", "udaipur.png")

MARBLE = MARBLE_SH = CREAM = TEAL = TEAL_DEEP = GOLD = GROUND = EARTH = None
ASPHALT = LINE = WATER = LEAF = LEAF_DK = TRUNK = GLASSY = CAR_A = CAR_B = BOAT = AWNING = None


def palette():
    global MARBLE, MARBLE_SH, CREAM, TEAL, TEAL_DEEP, GOLD, GROUND, EARTH
    global ASPHALT, LINE, WATER, LEAF, LEAF_DK, TRUNK, GLASSY, CAR_A, CAR_B, BOAT, AWNING
    MARBLE    = K.mat("ud_marble",    (0.965, 0.957, 0.937))
    MARBLE_SH = K.mat("ud_marble_sh", (0.855, 0.843, 0.812))
    CREAM     = K.mat("ud_cream",     (0.918, 0.867, 0.769))
    TEAL      = K.mat("ud_teal",      (0.243, 0.624, 0.710))
    TEAL_DEEP = K.mat("ud_teal_deep", (0.106, 0.310, 0.369))
    GOLD      = K.mat("ud_gold",      (0.851, 0.663, 0.263), roughness=0.3, metallic=0.55)
    GROUND    = K.mat("ud_ground",    (0.749, 0.722, 0.604))
    EARTH     = K.mat("ud_earth",     (0.600, 0.545, 0.443))
    ASPHALT   = K.mat("ud_asphalt",   (0.259, 0.278, 0.302))
    LINE      = K.mat("ud_line",      (0.949, 0.949, 0.933))
    WATER     = K.mat("ud_water",     (0.169, 0.451, 0.545), roughness=0.16)
    LEAF      = K.mat("ud_leaf",      (0.267, 0.545, 0.278))
    LEAF_DK   = K.mat("ud_leaf_dk",   (0.169, 0.412, 0.224))
    TRUNK     = K.mat("ud_trunk",     (0.376, 0.278, 0.196))
    GLASSY    = K.glass("ud_glass",   (0.275, 0.510, 0.600))
    CAR_A     = K.mat("ud_car_a",     (0.918, 0.910, 0.894))
    CAR_B     = K.mat("ud_car_b",     (0.796, 0.286, 0.243))
    BOAT      = K.mat("ud_boat",      (0.694, 0.502, 0.325))
    AWNING    = K.mat("ud_awning",    (0.851, 0.302, 0.267))


def lake(center=(-1.4, -1.6), dims=(9.4, 7.2)):
    """Lake Pichola. Deliberately oversized — the water is the subject here."""
    return K.water_patch("pichola", center, dims, WATER, EARTH, bank=0.22)


def lake_palace(origin=(-2.4, -2.3)):
    """Taj Lake Palace: a white marble block that fills its island edge to edge,
    so it reads as floating. Domed cupolas at the corners, arcades all round."""
    ox, oy = origin
    parts = []
    # island platform, barely wider than the palace
    parts.append(K.slab_on_ground("lp_island", (ox, oy), (3.1, 2.3), 0.14, MARBLE_SH, z0=0.03))
    parts.append(K.slab_on_ground("lp_terrace", (ox, oy), (2.9, 2.1), 0.1, MARBLE, z0=0.17))

    parts.append(K.slab_on_ground("lp_body", (ox, oy), (2.3, 1.6), 0.62, MARBLE, z0=0.27))
    parts += K.window_grid("lp_arc", (ox, oy - 0.8, 0.56), (0, -1), 2.2, 0.5, 1, 7,
                           TEAL_DEEP, inset=0.03, pad=0.1)
    parts.append(K.slab_on_ground("lp_band", (ox, oy), (2.42, 1.72), 0.07, MARBLE_SH, z0=0.89))

    parts.append(K.slab_on_ground("lp_upper", (ox, oy), (1.5, 1.1), 0.52, MARBLE, z0=0.96))
    parts += K.window_grid("lp_arc2", (ox, oy - 0.55, 1.2), (0, -1), 1.4, 0.4, 1, 5,
                           TEAL_DEEP, inset=0.03, pad=0.08)
    parts.append(K.slab_on_ground("lp_band2", (ox, oy), (1.62, 1.22), 0.06, MARBLE_SH, z0=1.48))

    # central dome plus four corner cupolas
    parts += K.onion_dome("lp_dome", (ox, oy, 1.54), 0.38, MARBLE, GOLD, height_scale=1.4)
    for sx, sy in ((-1.0, -0.66), (1.0, -0.66), (-1.0, 0.66), (1.0, 0.66)):
        parts += K.chhatri(f"lp_ch{sx}{sy}", (ox + sx, oy + sy, 0.96), 0.3, 0.2, MARBLE, GOLD)
    # jetty out to the water
    parts.append(K.box("lp_jetty", (ox + 1.85, oy, 0.12), (0.8, 0.3, 0.1), MARBLE_SH))
    return parts


def city_palace(origin=(3.0, 2.0)):
    """The shoreline facade: a long, high cream-and-marble wall of balconies with
    octagonal towers — Udaipur's landward silhouette."""
    ox, oy = origin
    parts = []
    parts.append(K.slab_on_ground("cp_plinth", (ox, oy), (5.2, 2.6), 0.5, MARBLE_SH))
    parts.append(K.slab_on_ground("cp_body", (ox, oy), (4.9, 2.3), 1.5, CREAM, z0=0.5))

    # two tiers of arcaded balconies down the lake-facing side
    for lvl, bz in enumerate((0.75, 1.35)):
        parts += K.window_grid(f"cp_w{lvl}", (ox, oy - 1.15, bz), (0, -1), 4.7, 0.46, 1, 11,
                               TEAL_DEEP, inset=0.035, pad=0.12)
        parts.append(K.box(f"cp_ledge{lvl}", (ox, oy - 1.2, bz - 0.26), (4.9, 0.14, 0.08),
                           MARBLE))
    parts.append(K.slab_on_ground("cp_cap", (ox, oy), (5.05, 2.45), 0.1, MARBLE, z0=2.0))

    # octagonal towers
    for sx in (-2.1, 0.0, 2.1):
        parts.append(K.cyl(f"cp_tw{sx}", (ox + sx, oy + 0.3, 2.35), 0.46, 0.72, MARBLE,
                           verts=8, smooth=False))
        parts += K.onion_dome(f"cp_twd{sx}", (ox + sx, oy + 0.3, 2.71), 0.42, MARBLE, GOLD,
                              height_scale=1.35)
    for sx in (-1.05, 1.05):
        parts += K.chhatri(f"cp_ch{sx}", (ox + sx, oy - 0.7, 2.1), 0.34, 0.24, MARBLE, GOLD)

    # ghat steps running down into the lake
    for i in range(4):
        parts.append(K.box(f"cp_ghat{i}", (ox, oy - 1.55 - i * 0.22, 0.32 - i * 0.07),
                           (5.0 - i * 0.2, 0.22, 0.64 - i * 0.14), MARBLE_SH))
    return parts


def jag_mandir(origin=(1.4, -4.0)):
    """The second island: lower, squarer, with one big dome and corner kiosks."""
    ox, oy = origin
    parts = []
    parts.append(K.slab_on_ground("jg_island", (ox, oy), (1.9, 1.5), 0.14, MARBLE_SH, z0=0.03))
    parts.append(K.slab_on_ground("jg_body", (ox, oy), (1.4, 1.1), 0.52, MARBLE, z0=0.17))
    parts += K.window_grid("jg_arc", (ox, oy - 0.55, 0.42), (0, -1), 1.3, 0.36, 1, 5,
                           TEAL_DEEP, inset=0.03, pad=0.08)
    parts += K.onion_dome("jg_dome", (ox, oy, 0.69), 0.34, MARBLE, GOLD, height_scale=1.35)
    for sx, sy in ((-0.62, -0.44), (0.62, -0.44), (-0.62, 0.44), (0.62, 0.44)):
        parts += K.chhatri(f"jg_ch{sx}{sy}", (ox + sx, oy + sy, 0.17), 0.26, 0.17, MARBLE, GOLD)
    # a row of cypress, which every Udaipur garden island has
    for i, dx in enumerate((-0.8, -0.45, 0.45, 0.8)):
        parts.append(K.cone(f"jg_cyp{i}", (ox + dx, oy + 0.62, 0.42), 0.11, 0.02, 0.5,
                            LEAF_DK, verts=8))
    return parts


def boats():
    """Shikara-style ferries — the moving specks that give the lake scale."""
    parts = []
    for i, (x, y, a) in enumerate(((-4.4, -0.9, 0.5), (-0.4, -4.4, -0.3),
                                   (-3.2, -4.6, 1.1), (0.4, -1.1, 2.4))):
        parts.append(K.box(f"bt{i}_hull", (x, y, 0.1), (0.62, 0.22, 0.1), BOAT, rot_z=a))
        parts.append(K.box(f"bt{i}_canopy", (x, y, 0.22), (0.34, 0.2, 0.06), AWNING, rot_z=a))
        parts.append(K.box(f"bt{i}_post", (x, y, 0.17), (0.3, 0.02, 0.1), BOAT, rot_z=a))
    return parts


def streets():
    parts = []
    parts += K.road("rd_h", (-6, 4.6), (6, 4.6), 1.3, ASPHALT, LINE)
    parts += K.kerb("kb_h", (-6, 4.6), (6, 4.6), 1.3, GROUND)
    parts += K.road("rd_v", (5.2, -6), (5.2, 4.0), 1.15, ASPHALT, LINE)
    for i, (pos, ang, m) in enumerate(((((-2.4, 4.85)), 0.0, CAR_A),
                                       ((1.6, 4.35), math.pi, CAR_B),
                                       ((5.45, -1.4), math.pi / 2, CAR_A),
                                       ((4.95, -4.0), -math.pi / 2, CAR_B))):
        parts += K.car(f"car{i}", pos, ang, m, GLASSY)
    return parts


def greenery():
    parts = []
    spots = [(-5.4, 3.4, 0.95), (-4.0, 3.2, 0.85), (-2.4, 3.1, 0.9), (0.2, 3.3, 0.8),
             (6.0, 1.0, 0.9), (6.1, -2.4, 0.85), (3.4, 5.5, 0.9), (-1.2, 5.6, 0.85),
             (-5.6, 5.5, 0.9), (6.2, 4.0, 0.8), (-5.8, 1.6, 0.85)]
    for i, (x, y, s) in enumerate(spots):
        parts += K.tree(f"tree{i}", (x, y), s, TRUNK, LEAF if i % 2 else LEAF_DK,
                        "palm" if i % 4 == 0 else "round")
    return parts


def build():
    K.clear_scene()
    palette()
    parts = []
    parts += K.base_slab(GROUND, EARTH)
    parts += lake()
    parts += streets()
    parts += city_palace()
    parts += lake_palace()
    parts += jag_mandir()
    parts += boats()
    parts += greenery()

    tile = K.join_all(parts, "udaipur_tile")
    K.export_glb(OUT_GLB, tile)
    K.setup_iso_render(span=15.0)
    K.render_preview(OUT_PNG)
    K.render_preview(OUT_POSTER, resolution=720, transparent=True)


if __name__ == "__main__":
    build()

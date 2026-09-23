"""
Jaisalmer — the Golden City.

Landmarks:
  * Jaisalmer Fort (Sonar Quila) — a living fort on the Trikuta hill, ringed by
    99 round bastions. The bastion ring on a raised plateau IS the silhouette.
  * Patwon Ki Haveli   — the five-mansion cluster of carved jharokha balconies.
  * Gadisar Lake       — tank with its chhatri gateway, the one patch of water.
  * Sam dunes + camels — the Thar, without which this is just a fort on a rock.

Build:
  /Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/blender/jaisalmer_tile.py
"""
import bpy
import math
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import tile_kit as K
import tile_details as D

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT_GLB = os.path.join(ROOT, "public", "models", "jaisalmer_tile.glb")
OUT_PNG = os.path.join(ROOT, "blender-output", "tiles", "jaisalmer_tile.png")
# Transparent poster shown in the card until the .glb finishes loading.
OUT_POSTER = os.path.join(ROOT, "public", "images", "tiles", "jaisalmer.png")

SAND = SAND_DEEP = GOLD_STONE = STONE_LIGHT = GROUND = EARTH = None
ASPHALT = LINE = WATER = LEAF = TRUNK = GLASSY = CAR_A = CAR_B = FLAG = CAMEL = None


def palette():
    global SAND, SAND_DEEP, GOLD_STONE, STONE_LIGHT, GROUND, EARTH
    global ASPHALT, LINE, WATER, LEAF, TRUNK, GLASSY, CAR_A, CAR_B, FLAG, CAMEL
    # Jaisalmer is built from the yellow sandstone it stands on, so the whole tile
    # is one warm family — the fort should read as growing out of the ground.
    GOLD_STONE  = K.mat("js_stone",      (0.851, 0.647, 0.271))
    SAND        = K.mat("js_sand",       (0.898, 0.776, 0.514))
    SAND_DEEP   = K.mat("js_sand_deep",  (0.706, 0.510, 0.216))
    STONE_LIGHT = K.mat("js_stone_lt",   (0.933, 0.831, 0.596))
    GROUND      = K.mat("js_ground",     (0.847, 0.741, 0.518))
    EARTH       = K.mat("js_earth",      (0.702, 0.580, 0.376))
    ASPHALT     = K.mat("js_asphalt",    (0.298, 0.282, 0.271))
    LINE        = K.mat("js_line",       (0.949, 0.933, 0.886))
    WATER       = K.mat("js_water",      (0.180, 0.420, 0.498), roughness=0.18)
    LEAF        = K.mat("js_leaf",       (0.396, 0.541, 0.290))
    TRUNK       = K.mat("js_trunk",      (0.427, 0.318, 0.212))
    GLASSY      = K.glass("js_glass",    (0.310, 0.545, 0.639))
    CAR_A       = K.mat("js_car_a",      (0.914, 0.906, 0.878))
    CAR_B       = K.mat("js_car_b",      (0.800, 0.302, 0.235))
    FLAG        = K.mat("js_flag",       (0.851, 0.231, 0.188))
    CAMEL       = K.mat("js_camel",      (0.776, 0.596, 0.400))


def fort(origin=(-2.7, 2.0), radius=2.6):
    """Sonar Quila: a plateau carrying a ring of round bastions and crenellated
    curtain wall, packed with sandstone houses and temple sikharas inside."""
    ox, oy = origin
    parts = []

    # The Trikuta hill: two stacked tapering drums so the fort sits up high.
    parts.append(K.cone("ft_hill", (ox, oy, 0.3), radius * 1.16, radius * 1.0, 0.6,
                        EARTH, verts=26, smooth=False))
    parts.append(K.cone("ft_scarp", (ox, oy, 0.82), radius * 1.0, radius * 0.94, 0.45,
                        SAND_DEEP, verts=26, smooth=False))

    wall_z = 1.04
    # Curtain wall ring
    parts.append(K.cyl("ft_wall", (ox, oy, wall_z + 0.3), radius * 0.95, 0.6,
                       GOLD_STONE, verts=26, smooth=False))
    parts.append(K.cyl("ft_wall_cap", (ox, oy, wall_z + 0.62), radius * 0.99, 0.09,
                       STONE_LIGHT, verts=26, smooth=False))

    # The 99 bastions, abbreviated to 14 — round drums pushed out of the wall.
    n_bastion = 18
    for i in range(n_bastion):
        a = K.TAU * i / n_bastion
        bx, by = ox + math.cos(a) * radius * 0.95, oy + math.sin(a) * radius * 0.95
        parts.append(K.cyl(f"ft_bast{i}", (bx, by, wall_z + 0.34), 0.34, 0.78,
                           GOLD_STONE, verts=24, smooth=True))
        parts.append(K.cyl(f"ft_bast_cap{i}", (bx, by, wall_z + 0.76), 0.4, 0.1,
                           STONE_LIGHT, verts=24, smooth=True))
        for band_z in (.10, .44, .65):
            parts.append(K.cyl(f"ft_course{i}", (bx, by, wall_z + band_z), .348, .032, SAND_DEEP, verts=24))
        for offset in (-.6, 0, .6):
            aa = a + offset
            parts += K.arch_window(f"ft_slit{i}_{offset}", (bx + math.cos(aa) * .342, by + math.sin(aa) * .342, wall_z + .48), (math.cos(aa), math.sin(aa)), .065, .16, STONE_LIGHT)
        # merlons crowning each bastion
        for j in range(6):
            aa = K.TAU * j / 6.0
            parts.append(K.box(f"ft_m{i}_{j}",
                               (bx + math.cos(aa) * 0.33, by + math.sin(aa) * 0.33,
                                wall_z + 0.88),
                               (0.12, 0.12, 0.16), GOLD_STONE))

    # Town inside the walls: dense flat-roofed sandstone houses.
    inner = radius * 0.72
    spots = [(0.0, 0.0, 0.95), (-0.95, 0.5, 0.7), (0.9, 0.55, 0.62),
             (-0.5, -0.95, 0.72), (0.75, -0.8, 0.56), (1.5, 0.05, 0.5),
             (-1.6, -0.15, 0.58), (0.15, 1.3, 0.66), (-0.9, 1.45, 0.48),
             (1.2, 1.3, 0.44), (0.45, -1.6, 0.5)]
    for i, (dx, dy, h) in enumerate(spots):
        if math.hypot(dx, dy) > inner:
            continue
        w = 0.62 + (i % 3) * 0.12
        parts.append(K.slab_on_ground(f"ft_h{i}", (ox + dx, oy + dy), (w, w * 0.88), h,
                                      GOLD_STONE if i % 2 else STONE_LIGHT, z0=wall_z + 0.5))
        parts.append(K.slab_on_ground(f"ft_h{i}_cap", (ox + dx, oy + dy),
                                      (w + 0.08, w * 0.88 + 0.08), 0.06,
                                      SAND_DEEP, z0=wall_z + 0.5 + h))
        parts += K.window_grid(f"ft_h{i}_w", (ox + dx, oy + dy - w * 0.44, wall_z + 0.5 + h * 0.55),
                               (0, -1), w * 0.85, h * 0.45, 1, 2, SAND_DEEP,
                               inset=0.028, pad=0.07)

    # Jain temple sikharas — the tiered spires above the roofline.
    for i, (dx, dy) in enumerate(((-0.35, 0.35), (0.55, -0.25))):
        bz = wall_z + 1.45
        for t in range(4):
            r = 0.3 - t * 0.06
            parts.append(K.cyl(f"ft_sik{i}_{t}", (ox + dx, oy + dy, bz + t * 0.2),
                               r, 0.2, STONE_LIGHT, verts=10, smooth=False))
        parts.append(K.dome(f"ft_sik{i}_top", (ox + dx, oy + dy, bz + 0.8), 0.13, SAND_DEEP))

    # Palace block over the main gate, with the fort's flag.
    parts.append(K.slab_on_ground("ft_gate", (ox, oy - radius * 0.86), (1.25, 0.7), 1.15,
                                  STONE_LIGHT, z0=wall_z + 0.5))
    parts += K.window_grid("ft_gate_w", (ox, oy - radius * 0.86 - 0.35, wall_z + 1.15),
                           (0, -1), 1.1, 0.5, 1, 3, SAND_DEEP, inset=0.03, pad=0.08)
    parts += K.chhatri("ft_gate_ch_l", (ox - 0.62, oy - radius * 0.86, wall_z + 1.65),
                       0.3, 0.2, STONE_LIGHT, GOLD_STONE)
    parts += K.chhatri("ft_gate_ch_r", (ox + 0.62, oy - radius * 0.86, wall_z + 1.65),
                       0.3, 0.2, STONE_LIGHT, GOLD_STONE)
    parts.append(K.cyl("ft_pole", (ox, oy, wall_z + 2.6), 0.03, 1.0, STONE_LIGHT, verts=6))
    parts.append(K.box("ft_flag", (ox + 0.22, oy, wall_z + 3.0), (0.4, 0.02, 0.24), FLAG))

    # Ramp road climbing to the gate.
    ramp = K.box("ft_ramp", (ox, oy - radius * 1.25, 0.55), (1.0, 1.9, 1.1), SAND_DEEP)
    for v in ramp.data.vertices:
        if v.co.z > 0:
            v.co.z = -0.55 + (v.co.y + 0.95) * 1.1 / 1.9
    parts.append(ramp)
    return parts


def patwon_haveli(origin=(3.1, 2.4)):
    """Five adjoining mansions, each face a lattice of carved jharokha balconies."""
    ox, oy = origin
    parts = []
    for i in range(5):
        x = ox - 1.35 + i * .66
        h = 1.75 - abs(i - 2) * 0.12
        parts.append(K.slab_on_ground(f"pw{i}_body", (x, oy), (0.64, 1.3), h, GOLD_STONE))
        # projecting balcony bands — the haveli's defining texture
        for lvl in range(3):
            bz = 0.3 + lvl * (h - 0.3) / 3.0
            parts.append(K.box(f"pw{i}_bal{lvl}", (x, oy - 0.72, bz + 0.09),
                               (0.62, 0.20, 0.045), STONE_LIGHT))
            parts += K.window_grid(f"pw{i}_w{lvl}", (x, oy - 0.66, bz + 0.1),
                                   (0, -1), 0.60, .36, 1, 2, STONE_LIGHT,
                                   inset=0.08, pad=0.025)
            parts += D.railing(f"pw{i}_rail{lvl}", (x - .28, oy - .82), (x + .28, oy - .82), bz + .12, STONE_LIGHT, .10)
        parts.append(K.slab_on_ground(f"pw{i}_cap", (x, oy), (.70, 1.4), 0.09,
                                      STONE_LIGHT, z0=h))
        parts += K.crenellation(f"pw{i}_cr", (x - .3, oy - 0.68), (x + .3, oy - 0.68),
                                h + 0.09, SAND_DEEP, merlon=0.1, gap=0.12, height=0.15)
    parts += K.chhatri("pw_ch", (ox, oy + 0.4, 1.6), 0.32, 0.22, STONE_LIGHT, SAND_DEEP)
    return parts


def gadisar_lake(origin=(2.6, -3.3)):
    """Rainwater tank with its arched gateway — Jaisalmer's only still water."""
    ox, oy = origin
    parts = []
    parts += K.water_patch("gd_water", (ox, oy), (4.0, 2.7), WATER, SAND_DEEP)
    # stepped ghats down to the water
    for i in range(3):
        parts.append(K.box(f"gd_step{i}", (ox, oy + 1.52 + i * 0.17, 0.05 + i * 0.035),
                           (4.2 - i * 0.35, 0.17, 0.07 + i * 0.03), STONE_LIGHT))
    # the tori gateway
    parts.append(K.box("gd_gate_l", (ox - 0.55, oy + 1.9, 0.34), (0.22, 0.24, 0.68), GOLD_STONE))
    parts.append(K.box("gd_gate_r", (ox + 0.55, oy + 1.9, 0.34), (0.22, 0.24, 0.68), GOLD_STONE))
    parts.append(K.box("gd_gate_top", (ox, oy + 1.9, 0.75), (1.45, 0.28, 0.16), STONE_LIGHT))
    parts += K.onion_dome("gd_gate_dome", (ox, oy + 1.9, 0.83), 0.26, GOLD_STONE, SAND_DEEP)
    parts += K.chhatri("gd_ch_l", (ox - 1.7, oy + 1.9, 0.0), 0.42, 0.26, STONE_LIGHT, GOLD_STONE)
    parts += K.chhatri("gd_ch_r", (ox + 1.7, oy + 1.9, 0.0), 0.42, 0.26, STONE_LIGHT, GOLD_STONE)
    return parts


def dunes_and_camels():
    """Sam dunes in the far corner with a camel train — the Thar in shorthand."""
    parts = []
    for i, (x, y, r, h) in enumerate(((-4.5, -3.6, 1.25, 0.2), (-3.2, -4.8, 1.0, 0.15),
                                      (-5.1, -5.0, 0.9, 0.12))):
        parts.append(D.dune(f"dune{i}", x, y, r, r * .72, h * 1.8, SAND))
    for i, (x, y) in enumerate(((-4.2, -2.5), (-3.5, -2.75), (-2.8, -3.0))):
        parts += D.camel(f"cam{i}", x, y, CAMEL)
    return parts


def streets():
    parts = []
    skip = [(-0.1, -1.55, 1.0)]
    parts += K.road("rd_v", (-0.1, -6), (-0.1, -1.55), 1.25, ASPHALT, LINE, layer=0, skip=skip)
    parts += K.road("rd_h", (-6, -1.55), (6, -1.55), 1.35, ASPHALT, LINE, layer=1, skip=skip)
    parts += K.kerb("kb_h_l", (-6, -1.55), (-1.1, -1.55), 1.35, GROUND)
    parts += K.kerb("kb_h_r", (0.9, -1.55), (6, -1.55), 1.35, GROUND)
    for i, (pos, ang, m) in enumerate((((-2.6, -1.28), 0.0, CAR_A), ((1.9, -1.82), math.pi, CAR_B),
                                       ((0.18, -3.6), -math.pi / 2, CAR_B),
                                       ((4.4, -1.28), 0.0, CAR_B))):
        parts += K.car(f"car{i}", pos, ang, m, GLASSY)
    return parts


def greenery():
    parts = []
    spots = [(-5.4, 0.2, 0.9), (-4.4, -0.6, 0.8), (1.2, -0.6, 0.85), (3.4, -0.7, 0.9),
             (5.3, 0.6, 0.8), (5.4, 3.9, 0.85), (1.3, 4.6, 0.9), (-5.2, 4.4, 0.8),
             (0.6, -5.4, 0.85), (4.9, -5.2, 0.8), (-1.5, -3.2, 0.75), (-1.6, -5.1, 0.8)]
    for i, (x, y, s) in enumerate(spots):
        parts += K.tree(f"tree{i}", (x, y), s, TRUNK, LEAF, "palm" if i % 3 == 0 else "scrub")
    return parts


def build():
    K.clear_scene()
    palette()
    parts = []
    parts += K.base_slab(GROUND, EARTH)
    parts += streets()
    parts += gadisar_lake()
    parts += fort()
    parts += patwon_haveli()
    parts += dunes_and_camels()
    parts += greenery()

    parts = D.enrich(parts, "jaisalmer", STONE_LIGHT, SAND_DEEP, LEAF, TRUNK)
    tile = K.join_all(parts, "jaisalmer_tile")
    K.export_glb(OUT_GLB, tile)
    K.setup_iso_render(span=15.0)
    K.render_preview(OUT_PNG)
    K.render_preview(OUT_POSTER, resolution=720, transparent=True)


if __name__ == "__main__":
    build()

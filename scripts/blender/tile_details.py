"""Architectural and landscape detail shared by the four destination builds."""
import math
import random

import tile_kit as K


def railing(name, start, end, z, stone, height=.16):
    length = math.dist(start, end)
    count = max(2, round(length / .12))
    parts = [K.rod(name + "_rail", (*start, z + height), (*end, z + height), .018, stone)]
    for i in range(count + 1):
        t = i / count
        x, y = start[0] * (1 - t) + end[0] * t, start[1] * (1 - t) + end[1] * t
        parts.append(K.cyl(name + "_baluster", (x, y, z + height / 2), .012, height, stone, 6))
    return parts


def terrace(name, center, dims, z, stone):
    x, y = center
    w, d = dims[0] / 2, dims[1] / 2
    pts = [(x - w, y - d), (x + w, y - d), (x + w, y + d), (x - w, y + d)]
    parts = []
    for i in range(4):
        parts += railing(name + str(i), pts[i], pts[(i + 1) % 4], z, stone)
    return parts


def streetlamp(name, x, y):
    iron = K.mat("street_iron", (.14, .16, .15), .4, .65)
    lamp = K.mat("street_light", (.95, .84, .59), .28)
    return [K.cyl(name + "_foot", (x, y, .045), .075, .09, iron, 10),
            K.cyl(name + "_post", (x, y, .42), .023, .8, iron, 8),
            K.box(name + "_lantern", (x, y, .85), (.10, .10, .15), lamp),
            K.cone(name + "_hood", (x, y, .96), .092, .018, .07, iron, 4)]


def boat(name, x, y, angle, wood, cloth):
    def p(a, b, c):
        return (x + math.cos(angle) * a - math.sin(angle) * b,
                y + math.sin(angle) * a + math.cos(angle) * b, c)
    outline = [(-.38, 0), (-.24, -.13), (.24, -.13), (.40, 0), (.24, .13), (-.24, .13)]
    verts = [p(a * scale, b * scale, z) for scale, z in ((.66, .075), (1, .17)) for a, b in outline]
    faces = [tuple(reversed(range(6))), tuple(range(6, 12))] + [(i, (i + 1) % 6, (i + 1) % 6 + 6, i + 6) for i in range(6)]
    parts = [K.mesh_object(name + "_hull", verts, faces, wood)]
    for a in (-.17, .17):
        for b in (-.1, .1):
            parts.append(K.rod(name + "_post", p(a, b, .17), p(a, b, .36), .012, wood))
    canopy_verts = [p(a, b, .36 + .035 * math.cos(b / .14 * math.pi / 2)) for a in (-.23, .23) for b in (-.14, -.07, 0, .07, .14)]
    parts.append(K.mesh_object(name + "_canopy", canopy_verts, [(i, i + 5, i + 6, i + 1) for i in range(4)], cloth))
    for a in (-.16, 0, .16):
        parts.append(K.box(name + "_seat", p(a, 0, .20), (.045, .22, .035), wood, angle))
    return parts


def dune(name, x, y, rx, ry, height, sand):
    verts, faces = [], []
    n = 24
    for j in range(n + 1):
        for i in range(n + 1):
            u, v = 2 * i / n - 1, 2 * j / n - 1
            envelope = max(0, 1 - u * u) ** 1.4 * max(0, 1 - v * v) ** 1.6
            z = height * envelope * (1 + .23 * math.sin(u * 3 + v * 2))
            z += .007 * math.sin(v * 65 + u * 3) * envelope
            verts.append((x + u * rx, y + v * ry, .01 + z))
    for j in range(n):
        for i in range(n):
            a = j * (n + 1) + i
            faces.append((a, a + 1, a + n + 2, a + n + 1))
    return K.mesh_object(name, verts, faces, sand, True)


def camel(name, x, y, skin):
    dark = K.mat("camel_shadow", (.15, .10, .065), .8)
    saddle = K.mat("camel_cloth", (.53, .15, .09), .88)
    parts = [K.ellipsoid(name + "_body", (x, y, .34), (.24, .105, .14), skin),
             K.ellipsoid(name + "_hump", (x - .04, y, .46), (.11, .09, .14), skin),
             K.tube(name + "_neck", [(x + .16, y, .35), (x + .25, y, .43), (x + .27, y, .65)], .048, skin, 10),
             K.ellipsoid(name + "_head", (x + .32, y, .66), (.10, .046, .049), skin),
             K.ellipsoid(name + "_saddle", (x - .04, y, .51), (.09, .10, .035), saddle)]
    for lx in (-.16, .14):
        for ly in (-.065, .065):
            parts.append(K.tube(name + "_leg", [(x + lx, y + ly, .31), (x + lx - .018, y + ly, .14), (x + lx + .02, y + ly, .035)], .018, skin))
            parts.append(K.ellipsoid(name + "_hoof", (x + lx + .025, y + ly, .026), (.035, .024, .018), dark))
    parts.append(K.tube(name + "_tail", [(x - .21, y, .36), (x - .29, y, .24), (x - .27, y, .15)], .012, skin))
    for s in (-1, 1):
        parts.append(K.ellipsoid(name + "_ear", (x + .28, y + s * .051, .70), (.025, .014, .03), skin))
        parts.append(K.ellipsoid(name + "_eye", (x + .34, y + s * .042, .679), (.007, .006, .007), dark))
    return parts


def leopard(name, pos, angle, skin, spots):
    x, y, z = pos
    def p(a, b, c):
        return (x + math.cos(angle) * a - math.sin(angle) * b,
                y + math.sin(angle) * a + math.cos(angle) * b, z + c)
    parts = [K.ellipsoid(name + "_body", p(0, 0, .10), (.28, .085, .095), skin, angle, 3),
             K.ellipsoid(name + "_shoulder", p(.19, 0, .13), (.09, .09, .11), skin, angle),
             K.ellipsoid(name + "_head", p(.29, 0, .19), (.092, .070, .080), skin, angle, 3),
             K.ellipsoid(name + "_muzzle", p(.355, 0, .167), (.042, .052, .036), skin, angle),
             K.ellipsoid(name + "_nose", p(.39, 0, .18), (.014, .02, .013), spots, angle)]
    for side in (-1, 1):
        parts.append(K.ellipsoid(name + "_ear", p(.265, side * .052, .251), (.03, .021, .039), spots, angle))
        parts.append(K.ellipsoid(name + "_eye", p(.341, side * .053, .214), (.010, .010, .010), spots))
        for a in (-.16, .16):
            parts.append(K.ellipsoid(name + "_leg", p(a + .05, side * .09, .034), (.11, .032, .030), skin, angle))
    tail = [p(-.23 - t * .35, .05 + math.sin(t * 3.3) * .12, .08 - t * .055) for t in [i / 10 for i in range(11)]]
    parts.append(K.tube(name + "_tail", tail, .022, skin, 8))
    rng = random.Random(73)
    for i in range(44):
        a = rng.uniform(-.22, .23)
        theta = rng.uniform(.1, math.pi - .1)
        b, c = math.cos(theta) * .083, .10 + math.sin(theta) * .092
        parts.append(K.ellipsoid(name + "_rosette", p(a, b, c), (.015, .010, .009), spots, angle))
    return parts


def enrich(parts, city, stone, earth, leaf, trunk):
    """Side facades, terrace balustrades and human-scale street furniture."""
    additions = []
    # Complete the sides that become visible as the site rotates the tile.
    for obj in list(parts):
        if obj.type != "MESH":
            continue
        name = obj.name
        if any(word in name for word in ("_body", "cm_base", "cm_t1", "cm_t2", "cm_t3", "lp_upper", "ah_upper")) and not name.startswith(("car", "cam", "lp_body" if city == "jawai" else "animal", "sheep", "cr")):
            xs = [v.co.x for v in obj.data.vertices]
            ys = [v.co.y for v in obj.data.vertices]
            zs = [v.co.z for v in obj.data.vertices]
            w, d, h = max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)
            if w < .8 or h < .3:
                continue
            x, y, z = obj.location
            for side in (-1, 1):
                additions += K.window_grid(name + "_side" + str(side), (x + side * w / 2, y, z), (side, 0), d * .92, h * .80, max(1, round(h / .55)), max(2, round(d / .35)), stone, pad=.035)
            additions += K.window_grid(name + "_back", (x, y + d / 2, z), (0, 1), w * .94, h * .80, max(1, round(h / .55)), max(3, round(w / .38)), stone, pad=.035)
            additions += terrace(name + "_terrace", (x, y), (w, d), z + h / 2 + .04, stone)
    if city in ("jaipur", "jaisalmer"):
        yy = -2.70 if city == "jaipur" else -.70
        for i, xx in enumerate((-5.45, -1.10, 1.40, 5.40)):
            additions += streetlamp("lantern" + str(i), xx, yy)
    elif city == "udaipur":
        for i, xx in enumerate((-5, -2.5, 0, 2.5)):
            additions += streetlamp("lakeside" + str(i), xx, 3.75)
        additions += railing("promenade", (-5.8, 2.22), (.3, 2.22), .10, stone, .21)
    if city != "jawai":
        # Pots and benches near promenades, outside building/traffic footprints.
        positions = {"jaipur": [(1.8, -4.8), (4.8, -3.5), (-5.2, 4.4)],
                     "jaisalmer": [(5.3, -4.7), (1.2, 4.6)],
                     "udaipur": [(-4.0, 2.6), (-2.7, 2.6), (-1.2, 2.6)]}[city]
        for i, (x, y) in enumerate(positions):
            additions.append(K.cone("pot", (x, y, .10), .065, .10, .18, earth, 12))
            additions += K.tree("planter" + str(i), (x, y), .55, trunk, leaf, "scrub")
            for j in range(3):
                additions.append(K.box("bench_slat", (x + .38, y + j * .037, .19), (.33, .028, .024), trunk))
            for dx in (.26, .50):
                additions.append(K.box("bench_leg", (x + dx, y + .037, .11), (.025, .11, .16), stone))
    return parts + additions

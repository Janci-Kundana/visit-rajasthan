"""The homepage's Hawa Mahal, built from the supplied frontal photo.

An architectural interpretation, not a surveyed reconstruction. All relief and
jali are mesh geometry; the packed plaster maps work in both Cycles and glTF.
Blender: --background --threads 6 --python-exit-code 1 --python this_file.py
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, os.path.dirname(__file__))
from tile_kit import clear_scene, mesh_object, join_all, export_glb
from tile_surfaces import material, field, bitmap, save_source

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
clear_scene()


def plaster(name, color):
    m = material(name, color, .84)
    m["surface_family"] = "plaster"
    shade, rough, normal = field("plaster")
    for node in m.node_tree.nodes:
        if node.type == "TEX_IMAGE":
            if "albedo" in node.image.name:
                node.image = bitmap(name + "_limewash", (1 + (shade[:, :, None] - 1) * .42) * np.array(color))
            elif "normal" in node.image.name:
                node.image = bitmap("hawa_plaster_normal", normal, True)
            else:
                node.image = bitmap("hawa_plaster_roughness", np.stack((np.ones_like(rough), rough, np.zeros_like(rough)), axis=-1), True)
        elif node.type == "NORMAL_MAP":
            node.inputs["Strength"].default_value = .16
    return m


MATS = [
    plaster("hawa_rose", (.85, .40, .18)),
    plaster("hawa_ochre", (.81, .35, .14)),
    plaster("hawa_sunlit", (.90, .46, .23)),
    plaster("hawa_lime_trim", (.88, .72, .52)),
    plaster("hawa_aged_moulding", (.60, .405, .265)),
    material("hawa_recess_shadow", (.14, .105, .075), .95),
    material("hawa_shutter_wood", (.13, .235, .195), .82),
    material("hawa_finial_gold", (.69, .49, .22), .48, .48),
    plaster("hawa_plinth", (.57, .34, .22)),
    # Street surfaces. tile_surfaces picks each texture family from the name.
    material("hawa_footway_paving", (.70, .56, .44), .86),
    material("hawa_kerb_stone", (.80, .72, .60), .8),
    material("hawa_street_asphalt", (.24, .225, .215), .92),
    material("hawa_road_line", (.86, .84, .78), .7),
]
ROSE, OCHRE, LIGHT, TRIM, AGED, DARK, GREEN, GOLD, BASE, PAVE, KERB, ASPHALT, PAINT = range(len(MATS))


class Detail:
    """Batch each architectural module, avoiding thousands of scene objects."""
    def __init__(self, name):
        self.name, self.vertices, self.faces, self.indices, self.smooth = name, [], [], [], []

    def mesh(self, verts, faces, mat, smooth=False):
        offset = len(self.vertices)
        self.vertices.extend(verts)
        self.faces.extend(tuple(offset + i for i in face) for face in faces)
        self.indices.extend([mat] * len(faces))
        self.smooth.extend([smooth] * len(faces))

    def box(self, center, dims, mat):
        x, y, z = center
        a, b, c = (d / 2 for d in dims)
        verts = [(x + i * a, y + j * b, z + k * c) for k in (-1, 1) for j in (-1, 1) for i in (-1, 1)]
        self.mesh(verts, [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)], mat)

    def prism(self, footprint, bottom, top, mat):
        n = len(footprint)
        verts = [(x, y, z) for z in (bottom, top) for x, y in footprint]
        self.mesh(verts, [tuple(reversed(range(n))), tuple(range(n, n * 2))] + [(i, (i+1)%n, (i+1)%n+n, i+n) for i in range(n)], mat)

    def rod(self, a, b, radius, mat, sides=6):
        a, b = Vector(a), Vector(b)
        tangent = (b - a).normalized()
        u = tangent.cross(Vector((0, 0, 1)))
        if u.length < .01:
            u = tangent.cross(Vector((0, 1, 0)))
        u.normalize()
        v = tangent.cross(u)
        verts = [tuple(p + radius * (math.cos(i * math.tau / sides) * u + math.sin(i * math.tau / sides) * v)) for p in (a, b) for i in range(sides)]
        # Ends terminate inside mouldings or ledges; omit their hidden caps.
        self.mesh(verts, [(i, (i+1)%sides, (i+1)%sides+sides, i+sides) for i in range(sides)], mat, True)

    def line(self, points, radius, mat):
        vertices, faces = [], []
        sides = 6
        for i, point in enumerate(points):
            tangent = (Vector(points[min(i+1,len(points)-1)]) - Vector(points[max(0,i-1)])).normalized()
            u = tangent.cross(Vector((0,1,0)))
            if u.length < .01:
                u = tangent.cross(Vector((0,0,1)))
            u.normalize()
            v = tangent.cross(u)
            vertices.extend(tuple(Vector(point)+radius*(math.cos(j*math.tau/sides)*u+math.sin(j*math.tau/sides)*v)) for j in range(sides))
            if i:
                faces.extend(((i-1)*sides+j,(i-1)*sides+(j+1)%sides,i*sides+(j+1)%sides,i*sides+j) for j in range(sides))
        self.mesh(vertices, faces, mat, True)

    def finish(self):
        obj = mesh_object(self.name, self.vertices, self.faces)
        for m in MATS:
            obj.data.materials.append(m)
        for polygon, index, smooth in zip(obj.data.polygons, self.indices, self.smooth):
            polygon.material_index = index
            polygon.use_smooth = smooth
        return obj


def arch_outline(w, h, cusped=True):
    r, spring = w / 2, h - w / 2
    points = [(-r, 0), (r, 0)]
    for i in range(43):
        t = math.pi * i / 42
        # Seven small cusps, like the cusped stone arches in the reference.
        radius = r * (1 - (.07 * (1 - math.cos(t * 14)) if cusped else 0))
        points.append((radius * math.cos(t), spring + radius * math.sin(t)))
    return points


def jali(d, p, w, h):
    """True diamond lattice, clipped to the arched opening. No transparency maps."""
    step = .084 if w > .7 else .072
    for slope in (-1, 1):
        for intercept in np.arange(-h-w, h+w, step*2):
            samples = []
            for z in np.linspace(.035, h-.025, 100):
                x = slope*z + intercept
                if abs(x) < w*.465 and (z < h-w/2 or x*x + (z-(h-w/2))**2 < (w*.47)**2):
                    samples.append((x, z))
            if len(samples) > 1:
                d.rod(p(*samples[0], .052), p(*samples[-1], .052), .018, LIGHT, 4)


def window(d, center, tangent, w, h, lattice=True, shutter=True):
    u = Vector((*tangent, 0))
    n = Vector((u.y, -u.x, 0))
    origin = Vector(center)
    def p(x, z, depth=.02):
        return tuple(origin + u * x + Vector((0, 0, z)) + n * depth)
    outline = arch_outline(w, h)
    d.mesh([p(x, z, .008) for x, z in outline], [tuple(range(len(outline)))], DARK)
    # Nested carved archivolts and recessed reveals.
    for expansion, depth, radius, mat in ((1.15, .025, .038, ROSE), (1.08, .08, .025, TRIM), (1.0, .061, .023, AGED)):
        points = [p(x*expansion, (z-h*.5)*expansion+h*.5, depth) for x, z in outline]
        d.line(points + points[:1], radius, mat)
    if lattice:
        jali(d, p, w, h)
    if shutter:
        # Small inset green shutters provide the subtle colour in the photograph.
        sw, sh = w*.21, h*.23
        for sx in (-w*.23, w*.23):
            verts = [p(sx-sw/2, .08, .085), p(sx+sw/2, .08, .085), p(sx+sw/2, sh+.08, .085), p(sx-sw/2, sh+.08, .085)]
            d.mesh(verts, [(0,1,2,3)], GREEN)
            d.line(verts + verts[:1], .018, TRIM)
            for j in range(1, 5):
                xx = sx-sw/2+sw*j/5
                d.rod(p(xx, .10, .092), p(xx, sh+.06, .092), .007, AGED, 4)
    d.rod(p(-w*.59, -.065, .11), p(w*.59, -.065, .11), .045, TRIM)


def finial(d, x, y, z, size=1):
    # Turned stone/gilt lotus finial, with a pointed top.
    profile = [(.095,0),(.10,.07),(.055,.12),(.075,.19),(.05,.25),(.026,.36),(.003,.48)]
    verts = [(x+radius*size*math.cos(i*math.tau/10), y+radius*size*math.sin(i*math.tau/10), z+height*size) for radius,height in profile for i in range(10)]
    faces = [(j*10+i, j*10+(i+1)%10, (j+1)*10+(i+1)%10, (j+1)*10+i) for j in range(len(profile)-1) for i in range(10)]
    d.mesh(verts, faces, GOLD)


def hood(d, x, front, z, w, depth, height, material=AGED):
    # Shallow arched chhajja, not an onion dome. Several projecting stone courses.
    for layer, (scale, rise, thick, mat) in enumerate(((1.0,0,.12,material),(1.08,.12,.10,TRIM),(.96,.22,.10,ROSE))):
        pts = []
        for i in range(25):
            t = math.pi*i/24
            pts.append((math.cos(t)*w*.5*scale, math.sin(t)*height+rise))
        section = pts + [(px,pz-thick) for px,pz in reversed(pts)]
        n = len(section)
        verts = [(x+px, y, z+pz) for y in (front-depth, front+.12) for px,pz in section]
        d.mesh(verts, [tuple(range(n)),tuple(reversed(range(n,n*2)))] + [(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)], mat)
    # Lotus petals / closely spaced dentils under the drip edge.
    for i in range(13):
        xx = (i/12-.5)*w*.92
        zz = height*math.sqrt(max(0,1-(xx/(w*.5))**2))
        d.box((x+xx,front-depth-.006,z+zz-.085),(.058,.06,.10),TRIM)


def bay(column, floor, z, h):
    wide = column % 2 == 0
    x = column*2.02
    w = 2.38 if wide else 1.26
    projection = .57 if wide else .80
    rear, front = -.24, -.24-projection
    d = Detail(f"Storey_{floor+1}_jharokha_{column:+03d}")
    # Hexagonal projecting bay with two visible angled window faces.
    footprint = [(x-w/2,rear+.10),(x-w/2,front+.28),(x-w*.32,front),(x+w*.32,front),(x+w/2,front+.28),(x+w/2,rear+.10)]
    body_top = z+h-.70
    d.prism(footprint,z+.18,body_top, [ROSE,OCHRE,LIGHT][(column+floor)%3])
    # Deep balcony brackets, a stepped apron, and alternating cream string courses.
    for offset, scale, thickness, mat in ((.03,1.06,.16,AGED),(.17,1.15,.10,TRIM),(.29,1.11,.09,ROSE),(.37,1.03,.055,TRIM)):
        enlarged = [(x+(px-x)*scale, rear+(py-rear)*scale) for px,py in footprint]
        d.prism(enlarged,z+offset,z+offset+thickness,mat)
    for sx in (-w*.37, 0, w*.37):
        # Corbel widens towards the ledge.
        for k in range(4):
            d.box((x+sx,front+.18-k*.055,z-.22+k*.09),(.12+k*.025,.18+k*.095,.11),AGED if k%2==0 else ROSE)
    # Cream pilasters on each fold of the projecting bay.
    for px,py in footprint[1:5]:
        d.rod((px,py-.018,z+.40),(px,py-.018,body_top-.02),.038,TRIM)
        for pz in (z+.43,body_top-.08):
            d.box((px,py,pz),(.12,.12,.09),TRIM)
    winh = max(.78,h-1.38)
    faces = list(zip(footprint[1:4],footprint[2:5]))
    for j,(a,b) in enumerate(faces):
        vx,vy=b[0]-a[0],b[1]-a[1]
        length=math.hypot(vx,vy)
        window(d,((a[0]+b[0])/2,(a[1]+b[1])/2,z+.56),(vx/length,vy/length),length*(.76 if j==1 else .69),winh,lattice=True,shutter=floor<4)
        # Rectangular painted frame around each arched panel.
        u=Vector((vx/length,vy/length,0)); c=Vector(((a[0]+b[0])/2,(a[1]+b[1])/2-.02,z+.51))
        for sign in (-1,1):
            p=c+u*(sign*length*.45)
            d.rod(p,p+Vector((0,0,winh+.18)),.014,TRIM,4)
    hood(d,x,front+.07,body_top+.01,w*1.17,.22,.56 if wide else .37)
    # Low scalloped parapet behind the chhajja gives a layered silhouette.
    for i in range(5 if wide else 3):
        px=x+(i/((4 if wide else 2))-.5)*w*.88
        finial(d,px,rear+.035,body_top+.20,.40)
    if floor>=3:
        finial(d,x,front+.04,body_top+(.80 if wide else .59),.82 if wide else .58)
    return d.finish()


parts=[]
base=Detail("Sandstone_plinth_and_stepped_facade")
for i in range(4):
    base.box((0,.9,-.20+i*.13),(43-i*.34,5.7-i*.25,.15),BASE if i%2==0 else AGED)

# The solid wall follows each storey's stepped shoulder, behind the jharokhas.
tiers=[(.42,4.12,7),(4.54,4.10,7),(8.64,4.05,7),(12.69,3.58,6),(16.27,3.00,4)]
for floor,(z,h,count) in enumerate(tiers):
    for column in range(-count,count+1):
        taper=0
        if floor==2:
            taper=max(0,abs(column)-5)*.38
        elif floor==3:
            taper=max(0,abs(column)-2)*.31
        elif floor==4:
            taper=abs(column)*.26
        height=h-taper
        # Continuous masonry behind upper tiers: the projecting balconies are
        # attached to one facade, including where the shoulder steps upward.
        wall_height = h+.10 if floor<4 and abs(column)<=tiers[floor+1][2] else height-.30
        base.box((column*2.02,.66,z+wall_height/2),(2.03,1.83,wall_height),ROSE)
        parts.append(bay(column,floor,z,height))
    # Continuous horizontal cornice connects the projecting window bays.
    for dz,depth,thick,mat in ((.08,.18,.13,AGED),(.24,.12,.045,TRIM),(.34,.07,.055,LIGHT)):
        base.box((0,-.28-depth/2,z+dz),((count*2+1)*2.02,depth,thick),mat)

# Long side wings, inset panels, roof balustrades, and open rooftop chhatris.
for sign in (-1,1):
    x=sign*18.05
    base.box((x,1.18,5.34),(5.50,2.8,10.35),OCHRE)
    base.box((x,-.27,1.52),(5.60,.35,2.50),ROSE)
    for z in (.44,2.88,3.02,10.52,10.70):
        base.box((x,-.45,z),(5.76,.32,.10),TRIM if z in (2.88,10.70) else AGED)
    for c in range(4):
        xx=x+(c-1.5)*1.30
        for zz in (1.25,4.1,5.75,7.4,9.02):
            window(base,(xx,-.245 if zz>3 else -.46,zz-.30),(1,0),.38 if zz>3 else .57,.58 if zz>3 else .93,False,False)
        for dx in (-.54,.54):
            base.rod((xx+dx,-.47,.53),(xx+dx,-.47,2.71),.019,TRIM,4)
    # Pierced terrace railing, with actual open arches.
    for c in range(21):
        xx=x-2.57+c*.257
        base.rod((xx,-.35,10.77),(xx,-.35,11.60),.028,TRIM)
        if c<20:
            points=[(xx+.129+.102*math.cos(i*math.pi/10),-.35,11.20+.18*math.sin(i*math.pi/10)) for i in range(11)]
            base.line(points,.022,TRIM)
    base.box((x,-.35,11.63),(5.7,.21,.12),TRIM)
    # Square chhatri with slender columns and a ribbed, shallow stone dome.
    cx=x+sign*1.1; cy=.55; bz=11.7
    base.box((cx,cy,bz),(2.75,2.55,.19),AGED)
    for dx in (-1.03,0,1.03):
        for dy in (-.95,.95):
            base.rod((cx+dx,cy+dy,bz),(cx+dx,cy+dy,bz+1.45),.065,TRIM,8)
            base.box((cx+dx,cy+dy,bz+1.35),(.23,.23,.17),LIGHT)
    base.box((cx,cy,bz+1.51),(2.90,2.65,.19),AGED)
    base.box((cx,cy,bz+1.67),(3.04,2.80,.12),TRIM)
    verts=[]
    for ring in range(9):
        t=math.pi*.5*ring/9
        for j in range(32):
            a=j*math.tau/32
            radius=1.31*math.cos(t)*(1+.018*math.cos(a*16))
            verts.append((cx+radius*math.cos(a),cy+radius*math.sin(a),bz+1.73+.68*math.sin(t)))
    verts.append((cx,cy,bz+2.42))
    faces=[(r*32+j,r*32+(j+1)%32,(r+1)*32+(j+1)%32,(r+1)*32+j) for r in range(8) for j in range(32)]
    faces += [(256+j,256+(j+1)%32,288) for j in range(32)]
    base.mesh(verts,faces,LIGHT)
    finial(base,cx,cy,bz+2.42,1.0)
parts.append(base.finish())

# Street frontage. The Pink City's walls continue either side of the palace and a
# road runs in front, so the plinth stands on something instead of the sky.
FOOTWAY=-.05      # buries the lowest plinth course
ROAD=-.20         # one kerb height below the footway
REACH=72          # fills ultrawide screens even at full pointer swing
WALL_FACE=-.1


def wall_arch(d,x,z,w,h,lattice=False):
    """A lighter arch than window(): dark opening, one cream moulding, optional jali."""
    def p(px,pz,depth=.02):
        return (x+px,WALL_FACE-depth,z+pz)
    outline=arch_outline(w,h)
    d.mesh([p(px,pz,.008) for px,pz in outline],[tuple(range(len(outline)))],DARK)
    ring=[p(px*1.08,(pz-h*.5)*1.08+h*.5,.05) for px,pz in outline]
    d.line(ring+ring[:1],.035,TRIM)
    if lattice:
        jali(d,p,w,h)


street=Detail("Street_and_footways")
# The near footway runs back under the plinth and walls, so no seam can show.
street.box((0,1.35,FOOTWAY-.3),(REACH*2,11.3,.6),PAVE)
street.box((0,-11.6,ROAD-.2),(REACH*2,14,.4),ASPHALT)
street.box((0,-39.45,FOOTWAY-.3),(REACH*2,41.1,.6),PAVE)
for y in (-4.45,-18.75):
    street.box((0,y,-.22),(REACH*2,.3,.36),KERB)
paint=ROAD+.006
for y in (-5.05,-18.15):
    street.box((0,y,paint),(REACH*2,.14,.012),PAINT)
# A zebra crossing in front of the palace; the centre line breaks for it.
for i in range(13):
    street.box((0,-5.6-i,paint),(4.4,.5,.012),PAINT)
for i in range(-12,12):
    if abs(i*6+3)>4:
        street.box((i*6+3,-11.6,paint),(3,.14,.012),PAINT)
# Sandstone bollards along the palace footway give the eye a near layer.
for i in range(17):
    x=-19.2+i*2.4
    if abs(x)>2.5:
        street.box((x,-3.95,FOOTWAY+.36),(.24,.24,.72),AGED)
        street.box((x,-3.95,FOOTWAY+.75),(.30,.30,.06),TRIM)
parts.append(street.finish())

# The Pink City wall either side: a shopfront arcade below, latticed windows under
# drip hoods above, and a crenellated parapet. Same plasters as the palace.
for sign in (-1,1):
    wall=Detail(f"City_wall_{'west' if sign<0 else 'east'}")
    x0,length=20.8,REACH-20.8
    mid=sign*(x0+length/2)
    wall.box((mid,1.15,3.2),(length,2.5,6.7),ROSE)
    wall.box((mid,-.1,.17),(length,.3,.56),BASE)
    wall.box((mid,-.13,.475),(length,.3,.05),AGED)
    wall.box((mid,-.2,3.62),(length,.22,.14),AGED)
    wall.box((mid,-.17,3.74),(length,.16,.08),TRIM)
    wall.box((mid,-.2,6.52),(length,.42,.16),AGED)
    wall.box((mid,.1,6.85),(length,.4,.5),ROSE)
    wall.box((mid,.1,7.13),(length,.48,.06),TRIM)
    bays=int((length-.6)/3.2)
    for k in range(bays+1):
        # A cream pilaster between shopfronts; every fourth, a full-height pier.
        px=sign*(x0+.3+k*3.2)
        if k%4==0:
            wall.box((px,-.24,3.25),(.9,.3,6.5),OCHRE)
        else:
            wall.box((px,-.16,1.95),(.18,.12,2.9),TRIM)
        if k==bays:
            break
        x=sign*(x0+.3+(k+.5)*3.2)
        wall_arch(wall,x,.5,2.0,2.9)
        if k%2:
            # A painted rolling shutter on every other shop.
            wall.box((x,-.13,1.45),(1.5,.03,1.9),GREEN)
            for j in range(1,6):
                wall.rod((x-.75,-.15,.5+j*.32),(x+.75,-.15,.5+j*.32),.012,AGED,4)
        wall_arch(wall,x,4.35,.78,1.3,lattice=True)
        hood(wall,x,WALL_FACE,5.78,1.05,.22,.26)
    # Kangura crenellations: merlons with pointed caps.
    for k in range(int(length/.85)):
        x=sign*(x0+.45+k*.85)
        wall.box((x,.1,7.36),(.42,.3,.4),ROSE)
        wall.mesh([(x-.21,-.05,7.56),(x+.21,-.05,7.56),(x+.21,.25,7.56),(x-.21,.25,7.56),(x,.1,7.8)],
                  [(0,1,4),(1,2,4),(2,3,4),(3,0,4)],TRIM)
    parts.append(wall.finish())

palace=join_all(parts,"hawa_mahal_home")
export_glb(os.path.join(ROOT,"blender-output","hawa_mahal_home.raw.glb"),palace)

# Resting view, shared with HomeScene.ts: a level perspective camera whose lens is
# shifted rather than tilted, so the facade's verticals stay vertical. The still
# covers more than any one screen; the page positions and crops it.
DISTANCE,EYE,REST_YAW=80,17.1,math.atan2(1.2,58)
LEFT,RIGHT,BOTTOM,TOP=-38,38,-13.5,21   # the still's extent on the facade plane
PX_PER_METRE=32
scene=bpy.context.scene
camera_data=bpy.data.cameras.new("Facade_camera")
camera_data.sensor_fit="HORIZONTAL"
camera_data.sensor_width=36
camera_data.lens=camera_data.sensor_width*DISTANCE/(RIGHT-LEFT)
camera_data.shift_x=(LEFT+RIGHT)/2/(RIGHT-LEFT)
camera_data.shift_y=((BOTTOM+TOP)/2-EYE)/(RIGHT-LEFT)
camera=bpy.data.objects.new("Facade_camera",camera_data)
scene.collection.objects.link(camera)
camera.location=(DISTANCE*math.sin(REST_YAW),-DISTANCE*math.cos(REST_YAW),EYE)
camera.rotation_euler=(math.pi/2,0,REST_YAW)
scene.camera=camera
scene.render.resolution_x=round((RIGHT-LEFT)*PX_PER_METRE)
scene.render.resolution_y=round((TOP-BOTTOM)*PX_PER_METRE)
scene.render.resolution_percentage=100
# The page places the still assuming exactly this frame, so fail the build if not.
corners=[c*(DISTANCE/-c.z) for c in camera_data.view_frame(scene=scene)]
xs,ys=[c.x for c in corners],[c.y+EYE for c in corners]
assert max(abs(min(xs)-LEFT),abs(max(xs)-RIGHT),abs(min(ys)-BOTTOM),abs(max(ys)-TOP))<1e-3,(xs,ys)
world=bpy.data.worlds.new("Jaipur_daylight")
world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(.48,.67,.91,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=.52
scene.world=world
sun_data=bpy.data.lights.new("Warm_afternoon_sun","SUN")
sun_data.energy=2.6
sun_data.angle=math.radians(5)
sun_data.color=(1,.86,.69)
sun=bpy.data.objects.new("Warm_afternoon_sun",sun_data)
scene.collection.objects.link(sun)
# Same direction as the sun in tileLighting.ts, so the still and the live view
# cast matching shadows as one fades into the other.
sun.location=(17.6,-26.4,39.6)
sun.rotation_euler=(Vector((0,0,0))-sun.location).to_track_quat("-Z","Y").to_euler()
scene.render.engine="CYCLES"
scene.cycles.samples=40
scene.cycles.use_denoising=True
scene.render.threads_mode="FIXED"
scene.render.threads=6
scene.render.film_transparent=True
# Lossy WebP keeps alpha at a fraction of a PNG's size for a still this large.
scene.render.image_settings.file_format="WEBP"
scene.render.image_settings.color_mode="RGBA"
scene.render.image_settings.quality=90
scene.view_settings.view_transform="AgX"
scene.view_settings.look="AgX - Medium High Contrast"
poster=os.path.join(ROOT,"public","images","home","hawa-mahal.webp")
os.makedirs(os.path.dirname(poster),exist_ok=True)
scene.render.filepath=poster
save_source(os.path.join(ROOT,"blender-output","scenes","hawa_mahal_home.blend"))
print(f"[home] {len(palace.data.polygons):,} triangles; rendering {poster}",flush=True)
bpy.ops.render.render(write_still=True)
print("[home] Finished",flush=True)

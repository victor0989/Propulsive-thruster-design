# -*- coding: utf-8 -*-
# FreeCAD macro: CubeSat_2U_with_RealisticThruster_Pro (Corregida)
# Autor: Víctor + Copilot
# Unidad: mm

import FreeCAD as App
import FreeCADGui as Gui
import Part
import math

DOC_NAME = "CubeSat_2U_Thruster_Pro"

# --------------------------------------------------------------------
# 0) Documento
# --------------------------------------------------------------------
doc = App.ActiveDocument
if doc is None or doc.Label != DOC_NAME:
    doc = App.newDocument(DOC_NAME)

# --------------------------------------------------------------------
# 1) Parámetros
# --------------------------------------------------------------------
bus_W, bus_H, bus_L = 100.0, 100.0, 227.0
wall, fillet = 1.6, 2.0

bulk_thk, bulk_z_offset = 3.0, 16.0
feed_pcd, feed_holes, feed_diam = 24.0, 4, 6.0

use_central_tube = True
tube_OD, tube_wall, tube_L = 70.0, 1.2, 160.0

thruster_mode = "ion"
chamber_OD, chamber_L = 60.0, 50.0
flange_OD, flange_thk, pcd, pcd_n, bolt_d = 78.0, 3.0, 66.0, 6, 3.0
cbore_d, cbore_depth = 6.0, 1.5

grid_screen_thk, grid_accel_thk, grid_gap, grid_opening = 1.2, 1.2, 1.5, 0.65
hall_channel_OD, hall_channel_ID, hall_channel_len, hall_lip = 72.0, 52.0, 12.0, 2.0

use_nozzle = True
nozzle_len = 32.0
nozzle_inlet_d = chamber_OD * 0.95
nozzle_throat_d = chamber_OD * 0.55
nozzle_exit_d = 14.0

coil_R, coil_r, coil_offset = 34.0, 4.0, chamber_L * 0.45

strut_w, strut_t, strut_clear = 6.0, 3.0, 6.0
eps = 0.2
cx, cy = bus_W / 2.0, bus_H / 2.0

# --------------------------------------------------------------------
# 2) Utilidades
# --------------------------------------------------------------------
def vec(x, y, z): return App.Vector(x, y, z)
def add_part(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

def make_hollow_box(outer_w, outer_h, outer_l, t):
    outer = Part.makeBox(outer_w, outer_h, outer_l, vec(0,0,0))
    inner = Part.makeBox(outer_w - 2*t, outer_h - 2*t, outer_l - 2*t, vec(t,t,t))
    return outer.cut(inner)

def make_hollow_cylinder(OD, L, t, base_vec):
    outer = Part.makeCylinder(OD/2.0, L, base_vec)
    inner = Part.makeCylinder(OD/2.0 - t, L, base_vec)
    return outer.cut(inner)

def make_pcd_holes(z0, through, n, dia, pcd_diam, cbore_diam=None, cbore_depth_val=0.0, extra=0.0):
    holes = []
    for i in range(n):
        ang = 2.0 * math.pi * i / n
        x = cx + (pcd_diam/2.0) * math.cos(ang)
        y = cy + (pcd_diam/2.0) * math.sin(ang)
        h = Part.makeCylinder(dia/2.0, through + extra, vec(x, y, z0 - extra/2.0))
        holes.append(h)
        if cbore_diam and cbore_depth_val > 0:
            cb = Part.makeCylinder(cbore_diam/2.0, cbore_depth_val + eps, vec(x, y, z0 - (cbore_depth_val + eps)))
            holes.append(cb)
    return Part.makeCompound(holes)

def make_nozzle_revolve(z0, L, d_inlet, d_throat, d_exit):
    r_in, r_th, r_ex = d_inlet/2.0, d_throat/2.0, d_exit/2.0
    z1 = z0 + L
    pts = [
        vec(r_in, 0, z0),
        vec((r_in+r_th)*0.6, 0, z0 + 0.22*L),
        vec(r_th, 0, z0 + 0.35*L),
        vec((r_th+r_ex)*0.5, 0, z0 + 0.70*L),
        vec(r_ex, 0, z1)
    ]
    spline = Part.BSplineCurve()
    spline.interpolate(pts)
    e1 = Part.Edge(spline)
    e2 = Part.makeLine(vec(r_ex,0,z1), vec(0,0,z1))
    e3 = Part.makeLine(vec(0,0,z1), vec(0,0,z0))
    e4 = Part.makeLine(vec(0,0,z0), vec(r_in,0,z0))
    wire = Part.Wire([e1,e2,e3,e4])
    face = Part.Face(wire)
    return face.revolve(vec(0,0,0), vec(0,0,1), 360.0)

def grid_points(x_plane):
    pts = []
    width_y = bus_H - 2*side_margin_y
    height_z = bus_L - 2*side_margin_z
    for r in range(grid_rows):
        z = side_margin_z + (height_z * (r/(grid_rows-1) if grid_rows>1 else 0))
        for c in range(grid_cols):
            y = side_margin_y + (width_y * (c/(grid_cols-1) if grid_cols>1 else 0))
            pts.append((y,z))
    return pts

def get_export_dir():
    if doc.FileName:
        import os
        return os.path.dirname(doc.FileName)
    import tempfile
    return tempfile.gettempdir()

# --------------------------------------------------------------------
# 3) Bus, bulkhead y tubo central
# --------------------------------------------------------------------
bus_shell = make_hollow_box(bus_W, bus_H, bus_L, wall)
bus_shell = bus_shell.makeFillet(fillet, bus_shell.Edges)
bus_obj = add_part(bus_shell, "BusShell")

front_inner_z = bus_L - wall
bulk_w, bulk_h = bus_W - 2*wall, bus_H - 2*wall
bulk_z = front_inner_z - bulk_z_offset - bulk_thk
bulk_plate = Part.makeBox(bulk_w, bulk_h, bulk_thk, vec(wall, wall, bulk_z))

# Feedthroughs
feedholes = []
for i in range(feed_holes):
    ang = 2.0 * math.pi * i / feed_holes
    x = cx + (feed_pcd/2.0)*math.cos(ang)
    y = cy + (feed_pcd/2.0)*math.sin(ang)
    h = Part.makeCylinder(feed_diam/2.0, bulk_thk+eps, vec(x,y,bulk_z-eps/2))
    feedholes.append(h)
bulk_plate = bulk_plate.cut(Part.makeCompound(feedholes))
bulk_obj = add_part(bulk_plate, "BulkheadInner")

# Tubo central
tube_obj = None
if use_central_tube:
    tube_base_z = front_inner_z - bulk_z_offset - tube_L
    tube = make_hollow_cylinder(tube_OD, tube_L, tube_wall, vec(cx, cy, tube_base_z))
    tube_obj = add_part(tube, "CentralTube")

# --------------------------------------------------------------------
# 4) Propulsor
# --------------------------------------------------------------------
chamber_base_z = bus_L
chamber = Part.makeCylinder(chamber_OD/2.0, chamber_L, vec(cx, cy, chamber_base_z))
flange_z0 = front_inner_z - flange_thk
flange = Part.makeCylinder(flange_OD/2.0, flange_thk+eps, vec(cx, cy, flange_z0))
pcd_holes = make_pcd_holes(front_inner_z, flange_thk + eps*2, pcd_n, bolt_d, pcd, cbore_d, cbore_depth, extra=eps)
flange = flange.cut(pcd_holes)
thruster_parts = [chamber, flange]

if thruster_mode.lower() == "ion":
    grid_free_d = chamber_OD*grid_opening
    z_grid_screen = chamber_base_z + chamber_L - grid_screen_thk
    z_grid_accel = z_grid_screen + grid_screen_thk + grid_gap

    screen = Part.makeCylinder(chamber_OD/2.0, grid_screen_thk, vec(cx,cy,z_grid_screen))
    screen = screen.cut(Part.makeCylinder(grid_free_d/2.0, grid_screen_thk+eps, vec(cx,cy,z_grid_screen-eps/2)))
    accel = Part.makeCylinder(chamber_OD/2.0, grid_accel_thk, vec(cx,cy,z_grid_accel))
    accel = accel.cut(Part.makeCylinder((grid_free_d*0.9)/2.0, grid_accel_thk+eps, vec(cx,cy,z_grid_accel-eps/2)))
    thruster_parts += [screen, accel]

elif thruster_mode.lower() == "hall":
    ch_z = chamber_base_z + chamber_L - hall_channel_len
    anulus_outer = Part.makeCylinder(hall_channel_OD/2.0, hall_channel_len, vec(cx,cy,ch_z))
    anulus_inner = Part.makeCylinder(hall_channel_ID/2.0, hall_channel_len+eps, vec(cx,cy,ch_z-eps/2))
    channel = anulus_outer.cut(anulus_inner)
    lip = Part.makeCylinder(hall_channel_OD/2.0, hall_lip, vec(cx,cy,chamber_base_z+chamber_L))
    lip = lip.cut(Part.makeCylinder((hall_channel_ID*0.95)/2.0, hall_lip+eps, vec(cx,cy,chamber_base_z+chamber_L-eps/2)))
    thruster_parts += [channel, lip]

coil = Part.makeTorus(coil_R, coil_r, vec(cx,cy,chamber_base_z+coil_offset), App.Vector(1,0,0))
thruster_parts.append(coil)

if use_nozzle:
    noz = make_nozzle_revolve(chamber_base_z+chamber_L, nozzle_len, nozzle_inlet_d, nozzle_throat_d, nozzle_exit_d)
    noz.translate(vec(cx,cy,0))
    thruster_parts.append(noz)

thruster = thruster_parts[0]
for shp in thruster_parts[1:]:
    thruster = thruster.fuse(shp)
thruster_obj = add_part(thruster, "ThrusterAssembly")

# --------------------------------------------------------------------
# 5) Soportes
# --------------------------------------------------------------------
struts = []
inner_x0, inner_y0 = wall + strut_clear, wall + strut_clear
inner_x1, inner_y1 = bus_W - wall - strut_clear - strut_w, bus_H - wall - strut_clear - strut_w
strut_z0 = bulk_z + bulk_thk
strut_len = (front_inner_z - strut_z0) - 0.5

for x in (inner_x0, inner_x1):
    for y in (inner_y0, inner_y1):
        s = Part.makeBox(strut_w, strut_t, strut_len, vec(x,y,strut_z0))
        struts.append(s)

sL = Part.makeBox(strut_t, strut_w, strut_len, vec(cx-18, wall+strut_clear, strut_z0))
sR = Part.makeBox(strut_t, strut_w, strut_len, vec(cx+18-strut_t, bus_H-wall-strut_clear-strut_w, strut_z0))
struts += [sL, sR]

struts_comp = Part.makeCompound(struts)
struts_obj = add_part(struts_comp, "ThrusterStruts")

# --------------------------------------------------------------------
# 6) Agrupación y visual
# --------------------------------------------------------------------
group = doc.addObject("App::DocumentObjectGroup", "CubeSat_2U_Pro")
for o in (bus_obj, bulk_obj, tube_obj, thruster_obj, struts_obj):
    if o: group.addObject(o)

doc.recompute()
try:
    bus_obj.ViewObject.ShapeColor = (0.75,0.75,0.78)
    bulk_obj.ViewObject.ShapeColor = (0.55,0.55,0.6)
    if tube_obj: tube_obj.ViewObject.ShapeColor = (0.6,0.6,0.65)
    thruster_obj.ViewObject.ShapeColor = (0.8,0.8,0.85)
    struts_obj.ViewObject.ShapeColor = (0.4,0.4,0.45)
    Gui.ActiveDocument.ActiveView.fitAll()
except Exception: pass

# --------------------------------------------------------------------
# 7) Rebajes paneles solares
# --------------------------------------------------------------------
add_panel_recess = True
panel_recess_depth, rail_keep, end_keep = 0.8, 8.5, 8.0
if add_panel_recess and bus_obj:
    recesses = [
        Part.makeBox(panel_recess_depth, bus_H-2*rail_keep, bus_L-2*end_keep, vec(bus_W-panel_recess_depth, rail_keep, end_keep)),
        Part.makeBox(panel_recess_depth, bus_H-2*rail_keep, bus_L-2*end_keep, vec(0, rail_keep, end_keep)),
        Part.makeBox(bus_W-2*rail_keep, panel_recess_depth, bus_L-2*end_keep, vec(rail_keep, bus_H-panel_recess_depth, end_keep)),
        Part.makeBox(bus_W-2*rail_keep, panel_recess_depth, bus_L-2*end_keep, vec(rail_keep,0,end_keep))
    ]
    recess_comp = Part.makeCompound(recesses)
    bus_obj.Shape = bus_obj.Shape.cut(recess_comp)
    bus_obj.Label = "BusShell (Solar recess)"
    try: bus_obj.ViewObject.ShapeColor = (0.75,0.75,0.78)
    except Exception: pass

doc.recompute()

# --------------------------------------------------------------------
# 8) Radiador lateral -Y
# --------------------------------------------------------------------
add_radiator = True
if add_radiator:
    rad_thk, rad_w, rad_L = 2.0, bus_W-2*rail_keep, bus_L*0.6
    rad_z0 = (bus_L - rad_L)/2.0
    rad_x0 = rail_keep
    standoff_d, standoff_h, standoff_hole_d, standoff_margin = 6.0, rad_thk+wall+1.0, 3.0, 10.0

    radiator = Part.makeBox(rad_w, rad_thk, rad_L, vec(rad_x0,-rad_thk,rad_z0))
    standoffs = [Part.makeCylinder(standoff_d/2.0, standoff_h, vec(rad_x0+dx,0-(standoff_h-wall),rad_z0+dz))
                 for dx in (standoff_margin, rad_w-standoff_margin)
                 for dz in (standoff_margin, rad_L-standoff_margin)]
    standoffs_comp = Part.makeCompound(standoffs)

    holes = [Part.makeCylinder(standoff_hole_d/2.0, rad_thk+wall+2.0, vec(rad_x0+dx,-rad_thk-1.0,rad_z0+dz))
             for dx in (standoff_margin, rad_w-standoff_margin)
             for dz in (standoff_margin, rad_L-standoff_margin)]
    holes_comp = Part.makeCompound(holes)

    radiator = radiator.fuse(standoffs_comp).cut(holes_comp)
    rad_obj = add_part(radiator, "RadiatorY-")
    try: rad_obj.ViewObject.ShapeColor = (0.2,0.3,0.7)
    except Exception: pass

doc.recompute()

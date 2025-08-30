# -*- coding: utf-8 -*-
# Macro FreeCAD: CubeSat 1U/2U corregido y estable
# Autor: Víctor + Copilot
# Requiere FreeCAD 0.20+
import FreeCAD as App
import Part
import math
import os

# -------------------------
# CONFIG
# -------------------------
CFG = {
    "variant":"2U",
    "X":100.0, "Y":100.0, "Z_1U":113.5, "Z_2U":227.0,
    "panel_thk":1.6, "rail_w":8.0, "rail_h":2.0,
    "pcb_size":95.0, "pcb_thk":1.6, "n_pcbs":7, "gap_z":12.0,
    "standoff_d":3.5, "standoff_h":10.0,
    "battery_size":[100,60,20],
    "propulsion":{"type":"resistojet","tank_d":42,"tank_L":110,"nozzle_L":15,"nozzle_throat":0.4},
    "antennas":[300.0,170.0],
    "fasteners":{"bcd":80.0,"hole_d":3.2,"depth":4.0},
    "materials":{"Al6061":2700,"Al7075":2810,"FR4":1900,"LiIon":2200,"Steel":7850,"Cell":2600}
}

# -------------------------
# DOC
# -------------------------
doc = App.newDocument("CubeSat2U")
App.setActiveDocument("CubeSat2U")
MM=1.0

def cube(X,Y,Z,cx=0,cy=0,cz=0,name="Cube"):
    box=Part.makeBox(X,Y,Z)
    obj=doc.addObject("Part::Feature",name)
    obj.Shape=box
    obj.Placement.Base=App.Vector(cx-X/2,cy-Y/2,cz-Z/2)
    return obj

def cylinder(d,h,axis="Z",cx=0,cy=0,cz=0,name="Cyl"):
    r=d/2
    cyl=Part.makeCylinder(r,h)
    obj=doc.addObject("Part::Feature",name)
    obj.Shape=cyl
    if axis=="Z":
        obj.Placement.Base=App.Vector(cx,cy,cz-h/2)
    elif axis=="Y":
        obj.Placement.Rotation=App.Rotation(App.Vector(1,0,0),90)
        obj.Placement.Base=App.Vector(cx,cy-h/2,cz)
    elif axis=="X":
        obj.Placement.Rotation=App.Rotation(App.Vector(0,1,0),90)
        obj.Placement.Base=App.Vector(cx-h/2,cy,cz)
    return obj

# -------------------------
# Raíles
# -------------------------
rails=[]
rail_pos=[(CFG["X"]/2-CFG["rail_w"]/2,CFG["Y"]/2-CFG["rail_w"]/2),
          (-CFG["X"]/2+CFG["rail_w"]/2,CFG["Y"]/2-CFG["rail_w"]/2),
          (CFG["X"]/2-CFG["rail_w"]/2,-CFG["Y"]/2+CFG["rail_w"]/2),
          (-CFG["X"]/2+CFG["rail_w"]/2,-CFG["Y"]/2+CFG["rail_w"]/2)]
for i,(cx,cy) in enumerate(rail_pos):
    r=cube(CFG["rail_w"],CFG["rail_w"],CFG["Z_2U"],cx=cx,cy=cy,cz=0,name=f"Rail_{i+1}")
    rails.append(r)

# Paneles
panels=[]
inX=CFG["X"]-2*CFG["rail_w"]
inY=CFG["Y"]-2*CFG["rail_w"]
panels.append(cube(CFG["panel_thk"],inY,CFG["Z_2U"],cx=+CFG["X"]/2-CFG["rail_w"]-CFG["panel_thk"]/2))
panels.append(cube(CFG["panel_thk"],inY,CFG["Z_2U"],cx=-CFG["X"]/2+CFG["rail_w"]+CFG["panel_thk"]/2))
panels.append(cube(inX,CFG["panel_thk"],CFG["Z_2U"],cy=+CFG["Y"]/2-CFG["rail_w"]-CFG["panel_thk"]/2))
panels.append(cube(inX,CFG["panel_thk"],CFG["Z_2U"],cy=-CFG["Y"]/2+CFG["rail_w"]+CFG["panel_thk"]/2))
panels.append(cube(inX,inY,CFG["panel_thk"],cz=+CFG["Z_2U"]/2-CFG["panel_thk"]/2))
panels.append(cube(inX,inY,CFG["panel_thk"],cz=-CFG["Z_2U"]/2+CFG["panel_thk"]/2))

# PCBs
pcbs=[]
z0=-CFG["Z_2U"]/2+12
for i in range(CFG["n_pcbs"]):
    pcb=cube(CFG["pcb_size"],CFG["pcb_size"],CFG["pcb_thk"],cz=z0+i*CFG["gap_z"],name=f"PCB_{i+1}")
    pcbs.append(pcb)

# Standoffs
standoffs=[]
offset=CFG["pcb_size"]/2-5
for sx in (+offset,-offset):
    for sy in (+offset,-offset):
        s=cylinder(CFG["standoff_d"],CFG["standoff_h"]+(CFG["n_pcbs"]-1)*CFG["gap_z"],cz=z0+(CFG["standoff_h"]+(CFG["n_pcbs"]-1)*CFG["gap_z"])/2)
        standoffs.append(s)

# Batería
bx,by,bz=CFG["battery_size"]
battery=cube(bx,by,bz,cz=z0-4,name="Battery")

# Propulsión
prop_objs=[]
tank=cylinder(CFG["propulsion"]["tank_d"],CFG["propulsion"]["tank_L"],cz=-CFG["Z_2U"]/2+CFG["panel_thk"]+CFG["propulsion"]["tank_L"]/2,name="Tank")
prop_objs.append(tank)
nzL=CFG["propulsion"]["nozzle_L"]
throat=CFG["propulsion"]["nozzle_throat"]
noz1=cylinder(throat,nzL*0.4,cz=-CFG["Z_2U"]/2-nzL*0.3)
noz2=cylinder(throat*3,nzL*0.6,cz=-CFG["Z_2U"]/2-nzL*0.8)
prop_objs.append(noz1)
prop_objs.append(noz2)

# Antenas
ants=[]
for i,L in enumerate(CFG["antennas"]):
    ax=(-CFG["X"]/2+CFG["rail_w"]+10) if i==0 else (+CFG["X"]/2-CFG["rail_w"]-10)
    ant=cylinder(1.2,L,axis="Y",cx=ax,cz=+CFG["Z_2U"]/2+2)
    ants.append(ant)

# -------------------------
# Unión final
# -------------------------
all_parts=rails+panels+pcbs+standoffs+[battery]+prop_objs+ants
assembly=Part.makeCompound([p.Shape for p in all_parts])
obj_assembly=doc.addObject("Part::Feature","CubeSat2U")
obj_assembly.Shape=assembly
doc.recompute()

# -------------------------
# TechDraw opcional
# -------------------------
try:
    import TechDraw
    page=doc.addObject('TechDraw::DrawPage','Page')
    template=doc.addObject('TechDraw::DrawSVGTemplate','Template')
    template.Template=App.getResourceDir()+'Mod/TechDraw/Templates/A4_LandscapeTD.svg'
    page.Template=template
    view=doc.addObject('TechDraw::DrawViewPart','View')
    view.Source=obj_assembly
    page.addView(view)
except:
    print("TechDraw no disponible")

# -------------------------
# Export STEP
# -------------------------
out_dir=os.path.join(App.getUserAppDataDir(),"CubeSat_exports")
if not os.path.exists(out_dir): os.makedirs(out_dir)
Part.export([obj_assembly],os.path.join(out_dir,"CubeSat2U.step"))
print("Macro ejecutada correctamente")

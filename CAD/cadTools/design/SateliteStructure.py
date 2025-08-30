# -*- coding: utf-8 -*-
# FreeCAD macro: CubeSat_2U_with_MicroHallThruster
# Autor: Víctor + Copilot
# Unidad: mm

import FreeCAD as App
import FreeCADGui as Gui
import Part

DOC_NAME = "CubeSat_IonThruster"

# Crear nuevo documento
if App.ActiveDocument is None:
    App.newDocument(DOC_NAME)
else:
    App.setActiveDocument(DOC_NAME)
doc = App.ActiveDocument

# ------------------------------
# 0. Parámetros globales
# ------------------------------
# Bus 2U
bus_length = 227
bus_width = 100
bus_height = 100
wall_thickness = 1.6
fillet_radius = 2

# Cilindro central
cyl_diam = 74
cyl_length = 190
cyl_wall = 1.2

# Bulkheads
bulkhead_diam = 94
bulkhead_thickness = 2.5

# Thruster (Micro Hall)
thruster_can_diam = 60
thruster_can_length = 50
thruster_flange_diam = 76
thruster_flange_thickness = 3
nozzle_exit_diam = 10
nozzle_length = 30
coil_major_radius = 35
coil_minor_radius = 5

# ------------------------------
# 1. Funciones de modelado
# ------------------------------
def create_bus():
    outer = Part.makeBox(bus_width, bus_height, bus_length)
    inner = Part.makeBox(bus_width - 2*wall_thickness,
                         bus_height - 2*wall_thickness,
                         bus_length - 2*wall_thickness)
    inner.translate(App.Vector(wall_thickness, wall_thickness, wall_thickness))
    shell = outer.cut(inner)
    return shell.makeFillet(fillet_radius, shell.Edges)

def create_central_cylinder():
    outer = Part.makeCylinder(cyl_diam/2, cyl_length)
    inner = Part.makeCylinder((cyl_diam/2) - cyl_wall, cyl_length)
    cyl_shell = outer.cut(inner)
    cyl_shell.translate(App.Vector(bus_width/2, bus_height/2, (bus_length - cyl_length)/2))
    return cyl_shell

def create_bulkheads():
    front = Part.makeCylinder(bulkhead_diam/2, bulkhead_thickness)
    rear = front.copy()
    front.translate(App.Vector(bus_width/2, bus_height/2, (bus_length - cyl_length)/2))
    rear.translate(App.Vector(bus_width/2, bus_height/2, (bus_length + cyl_length)/2 - bulkhead_thickness))
    return front, rear

def create_thruster():
    # Cámara de plasma
    chamber = Part.makeCylinder(thruster_can_diam/2, thruster_can_length,
                                App.Vector(bus_width/2, bus_height/2, bus_length))
    # Tobera
    nozzle = Part.makeCone(thruster_can_diam/2, nozzle_exit_diam/2, nozzle_length,
                           App.Vector(bus_width/2, bus_height/2, bus_length + thruster_can_length))
    # Brida
    flange = Part.makeCylinder(thruster_flange_diam/2, thruster_flange_thickness,
                               App.Vector(bus_width/2, bus_height/2, bus_length - thruster_flange_thickness))
    # Bobina magnética
    coil = Part.makeTorus(coil_major_radius, coil_minor_radius,
                          App.Vector(bus_width/2, bus_height/2, bus_length + thruster_can_length/2),
                          App.Vector(1, 0, 0))
    return chamber.fuse([nozzle, flange, coil])

def create_support_plate():
    plate = Part.makeBox(5, bus_height - 20, bus_height - 20,
                         App.Vector(bus_width - 5, 10, 10))
    return plate

# ------------------------------
# 2. Ensamblaje
# ------------------------------
bus_shell = create_bus()
central_cyl = create_central_cylinder()
bulk_front, bulk_rear = create_bulkheads()
thruster = create_thruster()
support_plate = create_support_plate()

assembly = bus_shell.fuse([central_cyl, bulk_front, bulk_rear, thruster, support_plate])

Part.show(assembly)
doc.recompute()
Gui.ActiveDocument.ActiveView.fitAll()

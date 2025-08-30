import FreeCAD as App
import Part

doc = App.newDocument("FusionPropulsion")

# --- Parámetros ---
bus_size = 1200   # mm
reactor_diam = 810
reactor_length = 1200

shield_diam = 1200
shield_thickness = 50

truss_length1 = 4000
truss_length2 = 8000
truss_diam = 200

nozzle_length = 8000
nozzle_exit_diam = 2000
nozzle_throat_diam = 400

tank_diam = 1200
tank_length = 5000

# --- Bus ---
bus = Part.makeBox(bus_size, bus_size, bus_size)

# --- Reactor ---
reactor = Part.makeCylinder(reactor_diam/2, reactor_length)
reactor.translate(App.Vector(bus_size/2, bus_size/2, 0))

# --- Blindaje ---
shield = Part.makeCylinder(shield_diam/2, shield_thickness)
shield.translate(App.Vector(bus_size/2, bus_size/2, bus_size))

# --- Truss ---
truss1 = Part.makeCylinder(truss_diam/2, truss_length1)
truss1.translate(App.Vector(bus_size/2, bus_size/2, bus_size+shield_thickness))

truss2 = Part.makeCylinder(truss_diam/2, truss_length2)
truss2.translate(App.Vector(bus_size/2, bus_size/2, bus_size+shield_thickness+truss_length1))

# --- Tobera magnética ---
nozzle = Part.makeCone(nozzle_throat_diam/2, nozzle_exit_diam/2, nozzle_length)
nozzle.translate(App.Vector(bus_size/2, bus_size/2, bus_size+truss_length1+truss_length2))

# --- Tanques ---
tank1 = Part.makeCylinder(tank_diam/2, tank_length)
tank1.translate(App.Vector(bus_size/2 - 700, bus_size/2, bus_size+truss_length1))

tank2 = Part.makeCylinder(tank_diam/2, tank_length)
tank2.translate(App.Vector(bus_size/2 + 700, bus_size/2, bus_size+truss_length1))

# --- Ensamblado ---
assembly = bus.fuse([reactor, shield, truss1, truss2, nozzle, tank1, tank2])

Part.show(assembly)
doc.recompute()

# -*- coding: utf-8 -*-
# Macro: NaveFusionParametrica
# Unidades: mm (FreeCAD internamente usa mm). Masas en kg usando densidades [kg/m^3].

import FreeCAD as App
import Part
from FreeCAD import Vector

try:
    import FreeCADGui as Gui
    GUI_AVAILABLE = True
except Exception:
    GUI_AVAILABLE = False

DOC_NAME = "NaveFusion"

# -----------------------------
# PARAMS (ajustables)
# -----------------------------
P = {
    "BUS_LEN": 1000.0,
    "BUS_W": 1200.0,
    "BUS_H": 1000.0,

    "DOME_LEN": 200.0,
    "DOME_OD": 1200.0,
    "DOME_ID": 800.0,

    "FUSION_LEN": 4000.0,
    "FUSION_D": 800.0,
    "REACTOR_LEN": 3000.0,
    "REACTOR_D": 800.0,

    "TANK_LEN": 8000.0,
    "TANK_D": 1000.0,

    "RAD_LEN": 3000.0,
    "RAD_W": 800.0,
    "RAD_T": 20.0,
    "RAD_CENTER_Y": 800.0,
    "RAD_BASE_Z": 200.0,
    "RAD_H": 1000.0,

    "PV_THICK_X": 30.0,
    "PV_H": 1200.0,
    "PV_HALF_SPAN": 4000.0,   # desde el eje
    "PV_MOUNT_X": 500.0,      # centrado en el bus

    "NOZZLE_LEN": 1500.0,
    "NOZZLE_D_OUT": 2000.0,
    "NOZZLE_D_IN": 800.0,

    "X_BUS_START": 0.0,
    "X_FUSION_START": 1000.0,
    "X_TANK_START": 5000.0,
    "X_NOZZLE_START": 11500.0,
}

# -----------------------------
# Tolerancias y materiales
# -----------------------------
TOL = {
    "Bus": 2.0,
    "PanelSolar": 5.0,
    "Radiador": 3.0,
    "Reactor": 0.5,
    "Tobera": 1.0,
    "Tanque": 4.0,
    "Domo": 0.5,
    "FusionShell": 1.0,
}

MAT = {
    "Al7075": 2810.0,
    "CFRP": 1600.0,
    "Ti": 4430.0,
    "Graphite": 1850.0,
    "W": 19300.0,
    "B4C": 2520.0,
    "Inconel": 8440.0,
    "AlLi": 2600.0,
    "MLI": 50.0,
}

# factor efectivo (porosidad/mezcla)
MAT_MAP = {
    "Bus": ("Al7075", 1.0),
    "PanelSolar_L": ("CFRP", 1.0),
    "PanelSolar_R": ("CFRP", 1.0),
    "Radiador_L": ("Ti", 0.7),
    "Radiador_R": ("Ti", 0.7),
    "FusionShell": ("Inconel", 1.0),
    "Reactor": ("W", 0.7),
    "Domo": ("W", 0.7),
    "Tanque": ("AlLi", 1.0),
    "Tobera": ("Inconel", 1.0),
}

EXTRA_MASS = {
    "Tanque_Propelente_kg": 1200.0,  # masa húmeda adicional (propelente)
}

# -----------------------------
# Utilidades
# -----------------------------
def ensure_doc():
    doc = App.ActiveDocument
    if not doc or doc.Name != DOC_NAME:
        if doc:
            App.closeDocument(doc.Name)
        doc = App.newDocument(DOC_NAME)
    return doc

def add_obj(doc, shape, name, color=None):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    if GUI_AVAILABLE and color:
        obj.ViewObject.ShapeColor = color
    return obj

def set_props(obj, material_key, tol_mm):
    obj.addProperty("App::PropertyString", "Material", "Design").Material = material_key
    dens = MAT.get(material_key, 1000.0)
    obj.addProperty("App::PropertyFloat", "Density_kg_m3", "Design").Density_kg_m3 = dens
    obj.addProperty("App::PropertyFloat", "Tolerance_mm", "Design").Tolerance_mm = tol_mm
    vol_m3 = obj.Shape.Volume / 1e9  # mm^3 a m^3
    factor = MAT_MAP.get(obj.Name, (material_key, 1.0))[1]
    mass = dens * vol_m3 * factor
    obj.addProperty("App::PropertyFloat", "Mass_geom_kg", "Design").Mass_geom_kg = mass
    return mass

def cyl_along_x(radius, length, base_x, center_y, center_z):
    # cilindro por defecto en Z, lo rotamos a X
    cyl = Part.makeCylinder(radius, length)
    cyl.Placement = App.Placement(Vector(0,0,0), App.Rotation(Vector(0,1,0), 90))
    cyl.translate(Vector(base_x, center_y, center_z))
    return cyl

def cone_along_x(r1, r2, length, base_x, center_y, center_z):
    cone = Part.makeCone(r1, r2, length)
    cone.Placement = App.Placement(Vector(0,0,0), App.Rotation(Vector(0,1,0), 90))
    cone.translate(Vector(base_x, center_y, center_z))
    return cone

# -----------------------------
# Construcción
# -----------------------------
doc = ensure_doc()
assembly = doc.addObject("App::Part", "Nave")

def add_to_assembly(obj):
    try:
        assembly.addObject(obj)
    except Exception:
        pass

# Bus
bus = Part.makeBox(P["BUS_LEN"], P["BUS_W"], P["BUS_H"])
bus.translate(Vector(P["X_BUS_START"], -P["BUS_W"]/2.0, 0))
o_bus = add_obj(doc, bus, "Bus", color=(0.80, 0.80, 0.85))
add_to_assembly(o_bus)

# Carcasa de fusión
fusion_shell = cyl_along_x(P["FUSION_D"]/2.0, P["FUSION_LEN"], P["X_FUSION_START"], 0.0, P["BUS_H"]/2.0)
o_fusion = add_obj(doc, fusion_shell, "FusionShell", color=(0.70, 0.70, 0.75))
add_to_assembly(o_fusion)

# Domo (anillo)
outer = cyl_along_x(P["DOME_OD"]/2.0, P["DOME_LEN"], P["X_FUSION_START"], 0.0, P["BUS_H"]/2.0)
inner = cyl_along_x(P["DOME_ID"]/2.0, P["DOME_LEN"], P["X_FUSION_START"], 0.0, P["BUS_H"]/2.0)
domo = outer.cut(inner)
o_domo = add_obj(doc, domo, "Domo", color=(0.50, 0.50, 0.52))
add_to_assembly(o_domo)

# Reactor
reactor = cyl_along_x(P["REACTOR_D"]/2.0, P["REACTOR_LEN"], P["X_FUSION_START"] + 500.0, 0.0, P["BUS_H"]/2.0)
o_reactor = add_obj(doc, reactor, "Reactor", color=(0.40, 0.40, 0.45))
add_to_assembly(o_reactor)

# Tanque
tank = cyl_along_x(P["TANK_D"]/2.0, P["TANK_LEN"], P["X_TANK_START"], 0.0, P["BUS_H"]/2.0)
o_tank = add_obj(doc, tank, "Tanque", color=(0.75, 0.80, 0.85))
add_to_assembly(o_tank)

# Radiadores
def make_radiator(sign=+1):
    rad = Part.makeBox(P["RAD_LEN"], P["RAD_W"], P["RAD_T"])
    x0 = P["X_FUSION_START"] + (P["FUSION_LEN"] - P["RAD_LEN"]) / 2.0
    y0 = sign * (P["RAD_CENTER_Y"] - P["RAD_W"]/2.0)
    z0 = P["RAD_BASE_Z"]
    rad.translate(Vector(x0, y0, z0))
    return rad

rad_L = make_radiator(+1)
rad_R = make_radiator(-1)
o_rad_L = add_obj(doc, rad_L, "Radiador_L", color=(0.90, 0.20, 0.20))
o_rad_R = add_obj(doc, rad_R, "Radiador_R", color=(0.90, 0.20, 0.20))
add_to_assembly(o_rad_L)
add_to_assembly(o_rad_R)

# Paneles solares (cada ala crece en +Y; la derecha se desplaza hacia -Y)
pv_span_each = P["PV_HALF_SPAN"] - P["BUS_W"]/2.0  # 4000 - 600 = 3400 mm

def make_pv(sign=+1):
    pv = Part.makeBox(P["PV_THICK_X"], pv_span_each, P["PV_H"])
    x0 = P["PV_MOUNT_X"] - P["PV_THICK_X"]/2.0
    if sign > 0:
        # izquierda (+Y): arranca en el lateral del bus y crece +Y
        y0 = P["BUS_W"]/2.0
    else:
        # derecha (-Y): arranca fuera hacia -Y para que crezca +Y hasta el lateral
        y0 = -P["BUS_W"]/2.0 - pv_span_each
    z0 = 0.0
    pv.translate(Vector(x0, y0, z0))
    return pv

pv_L = make_pv(+1)
pv_R = make_pv(-1)
o_pv_L = add_obj(doc, pv_L, "PanelSolar_L", color=(0.10, 0.30, 0.60))
o_pv_R = add_obj(doc, pv_R, "PanelSolar_R", color=(0.10, 0.30, 0.60))
add_to_assembly(o_pv_L)
add_to_assembly(o_pv_R)

# Tobera magnética
nozzle = cone_along_x(P["NOZZLE_D_OUT"]/2.0, P["NOZZLE_D_IN"]/2.0, P["NOZZLE_LEN"], P["X_NOZZLE_START"], 0.0, P["BUS_H"]/2.0)
o_nozzle = add_obj(doc, nozzle, "Tobera", color=(0.30, 0.35, 0.40))
add_to_assembly(o_nozzle)

# -----------------------------
# Propiedades: materiales, tolerancias, masas
# -----------------------------
total_geom_mass = 0.0

def apply_props(o, default_mat_key, tol_key):
    global total_geom_mass
    tol = TOL.get(tol_key, 1.0)
    mkey = MAT_MAP.get(o.Name, (default_mat_key, 1.0))[0]
    total_geom_mass += set_props(o, mkey, tol)

apply_props(o_bus, "Al7075", "Bus")
apply_props(o_pv_L, "CFRP", "PanelSolar")
apply_props(o_pv_R, "CFRP", "PanelSolar")
apply_props(o_rad_L, "Ti", "Radiador")
apply_props(o_rad_R, "Ti", "Radiador")
apply_props(o_fusion, "Inconel", "FusionShell")
apply_props(o_reactor, "W", "Reactor")
apply_props(o_domo, "W", "Domo")
apply_props(o_tank, "AlLi", "Tanque")
apply_props(o_nozzle, "Inconel", "Tobera")

# Masa adicional de propelente para el tanque
o_tank.addProperty("App::PropertyFloat", "ExtraMass_kg", "Design").ExtraMass_kg = EXTRA_MASS["Tanque_Propelente_kg"]
o_tank.addProperty("App::PropertyFloat", "WetMass_kg", "Design").WetMass_kg = o_tank.Mass_geom_kg + o_tank.ExtraMass_kg

# Totales
total_mass_with_propellant = total_geom_mass + EXTRA_MASS["Tanque_Propelente_kg"]
assembly.addProperty("App::PropertyFloat", "TotalGeomMass_kg", "Summary").TotalGeomMass_kg = total_geom_mass
assembly.addProperty("App::PropertyFloat", "TotalWithPropellant_kg", "Summary").TotalWithPropellant_kg = total_mass_with_propellant

# -----------------------------
# Visual: aplicar sombreado solo a objetos que lo soporten
# -----------------------------
if GUI_AVAILABLE:
    for obj in doc.Objects:
        if hasattr(obj, "ViewObject") and hasattr(obj.ViewObject, "listDisplayModes"):
            modes = obj.ViewObject.listDisplayModes()
            if isinstance(modes, (list, tuple)) and "Shaded" in modes:
                obj.ViewObject.DisplayMode = "Shaded"
    try:
        Gui.ActiveDocument.ActiveView.fitAll()
    except Exception:
        pass

doc.recompute()

print("=== Resumen de masas ===")
print(f"Masa geométrica total [kg]: {total_geom_mass:.1f}")
print(f"Masa total con propelente [kg]: {total_mass_with_propellant:.1f}")
print(f"Tanque (seca) [kg]: {o_tank.Mass_geom_kg:.1f} | Propelente [kg]: {o_tank.ExtraMass_kg:.1f} | Húmeda [kg]: {o_tank.WetMass_kg:.1f}")
